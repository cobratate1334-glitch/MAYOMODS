"""Read actual finance APIs, show a common-scale graph and a bounded FX wallet."""
from native_hooks import h
from era_life1121.transactions import bits
from school_finance1125.catalog import CURRENCIES

def install(b):
 year=b.old['v45_current_year']['stub'];bank=b.old['era1121_actual_bank']['stub']
 # Native bank denomination remains authoritative. Exchange quotes are against
 # that denomination, not a silently relabelled one-dollar amount.
 code='str xzr,[sp]\nmov w25,#10000\nmov x0,xzr\nbl 0x2a73334\ncbz x0,base_rate1125\nmov x8,x0\n'+h.compare_key('£','base_gbp1125','base_eur_check1125')+'\nbase_eur_check1125:\n'+h.compare_key('€','base_eur1125','base_rate1125')+'\nbase_gbp1125:\nmov w25,#7800\nb base_rate1125\nbase_eur1125:\nmov w25,#9200\nbase_rate1125:\nstr x25,[sp]\nb finish'
 base_rate=b.routine('school1125_bank_currency_rate',code)
 # Selection follows the hero's actual residence/year; old currencies are
 # distinct IDs, so saved wallets never get renamed to a successor currency.
 code='str xzr,[sp]\n'+b.ctx('life_rework')+f'bl {year:#x}\nmov w26,w0\n'+h.load_game()+'\nldr x0,[x8,#0x28]\ncbz x0,local_default1125\nmov x1,xzr\nbl 0x2c38288\ncbz x0,local_default1125\nmov x1,xzr\nbl 0x2a27280\ncbz x0,local_default1125\nldr x27,[x0,#0x10]\ncbz x27,local_default1125\n'
 for n,iso,symbol,rate,countries,lo in sorted(CURRENCIES,key=lambda r:r[5],reverse=True):
  code+=f'cmp w26,#{lo}\nb.lt local_next1125_{n}\nmov x8,x27\n'
  for i,country in enumerate(countries):code+=h.compare_key(country,f'local_yes1125_{n}',f'local_country1125_{n}_{i}')+f'\nlocal_country1125_{n}_{i}:\n'
  code+=f'b local_next1125_{n}\nlocal_yes1125_{n}:\nmov w9,#{n}\nstr x9,[sp]\nb finish\nlocal_next1125_{n}:\n'
 code+='local_default1125:\nmov w9,#1\nstr x9,[sp]\nb finish'
 local=b.routine('school1125_residence_currency',code)
 # Read-only report: income includes spouse, outflow includes the game's own
 # monthly living costs/tax/debt calculations. It is a projection, not a fake
 # transaction ledger. Both bars use the same maximum.
 code=b.ctx('life_rework')+f'bl {bank:#x}\ncbz x0,finish\nmov x27,x0\nmov w1,#1\nmov x2,xzr\nbl 0x2a6f14c\nstr d0,[sp,#80]\nmov x0,x27\nmov x1,xzr\nbl 0x2a717ec\nfcvt d0,s0\n'+bits('x9',12.)+'fmov d1,x9\nfmul d0,d0,d1\nstr d0,[sp,#88]\n'+f'bl {base_rate:#x}\nmov w25,w0\nbl {local:#x}\nmov w26,w0\n'+b.put('FinCurrency1125','w26')
 for n,iso,symbol,rate,countries,lo in CURRENCIES:
  code+=f'cmp w26,#{n}\nb.ne report_next1125_{n}\n'+b.text('FinUnit1125',iso if iso!='AUDp'else'Australian pound')+f'mov w9,#{rate}\nstr w9,[sp,#96]\nb report_amounts1125\nreport_next1125_{n}:\n'
 code+='report_amounts1125:\nldr w9,[sp,#96]\nucvtf d2,w9\nucvtf d3,w25\nfdiv d2,d2,d3\nstr d2,[sp,#104]\n'
 for key,off in [('FinIncomeText1125',80),('FinExpenseText1125',88)]:
  code+=f'ldr d0,[sp,#{off}]\nldr d2,[sp,#104]\nfmul d0,d0,d2\nadd x0,sp,#128\nmov w1,#96\nadr x2,{b.literal("%.2f"):#x}\nbl {b.snprintf:#x}\nadd x0,sp,#128\nbl {h.NEW_STRING:#x}\nmov x28,x0\n'+b.textptr(key,'x28')
 code+='ldr d0,[sp,#80]\nldr d1,[sp,#88]\nfmax d2,d0,d1\nfmov d3,#1.0\nfmax d2,d2,d3\n'+bits('x9',100.)+'fmov d3,x9\nfmul d0,d0,d3\nfdiv d0,d0,d2\nfcvtzs w24,d0\nstr w24,[sp,#112]\nldr d0,[sp,#88]\nfmul d0,d0,d3\nfdiv d0,d0,d2\nfcvtzs w24,d0\nstr w24,[sp,#116]\nldr w24,[sp,#112]\n'+b.put('FinIncomeBar1125')+'ldr w24,[sp,#116]\n'+b.put('FinExpenseBar1125')+b.text('FinStatus1125','Current yearly projection. Income includes your spouse. Expenses are the monthly household outflow × 12, including living costs, taxes and loan payments. The bars share one scale; figures are shown in the local currency using offline game rates.')+'b finish'
 report=b.routine('school1125_finance_report',code)
 # A chosen wallet can be quoted/sold while abroad; zero follows residence.
 code='str xzr,[sp]\n'+b.ctx('life_rework')+b.get('FXSelected1125','w27')+f'bl {year:#x}\nmov w25,w0\n'
 for n,iso,symbol,rate,countries,lo in CURRENCIES:code+=f'cmp w27,#{n}\nb.ne fx_target_next1125_{n}\ncmp w25,#{lo}\nb.lt fx_target_local1125\nstr x27,[sp]\nb finish\nfx_target_next1125_{n}:\n'
 code+=f'fx_target_local1125:\nbl {local:#x}\nstr x0,[sp]\nb finish'
 target=b.routine('school1125_selected_wallet',code)
 # Fixed, disclosed game rates; 2% fee at BOTH exchange boundaries. Each wallet
 # stores actual foreign minor units. Reopening/country changes never mint cash.
 code='mov w20,w0\n'+b.ctx('life_rework')+b.text('FXStatus1125','No money changed.')+f'bl {target:#x}\nmov w26,w0\nbl {base_rate:#x}\nmov w25,w0\nbl {bank:#x}\ncbz x0,finish\nmov x27,x0\n'+f'bl {b.old["era1121_nominal_pay_factor"]["stub"]:#x}\nmov w28,w0\n'
 for n,iso,symbol,rate,countries,lo in CURRENCIES:
  code+=f'cmp w26,#{n}\nb.ne wallet_next1125_{n}\n'+b.get('FXWallet1125_'+str(n),'w19')+f'mov w9,#{rate}\nucvtf d2,w9\nucvtf d3,w25\nfdiv d2,d2,d3\nstr d2,[sp,#80]\n'+f'fmov d0,d2\nadd x0,sp,#128\nmov w1,#96\nadr x2,{b.literal("1 bank unit = %.4f "+iso):#x}\nbl {b.snprintf:#x}\nadd x0,sp,#128\nbl {h.NEW_STRING:#x}\nmov x24,x0\n'+b.textptr('FXQuote1125','x24')+'ucvtf d0,w28\n'+bits('x9',.1)+f'fmov d1,x9\nfmul d0,d0,d1\nadd x0,sp,#128\nmov w1,#96\nadr x2,{b.literal("%.2f bank units"):#x}\nbl {b.snprintf:#x}\nadd x0,sp,#128\nbl {h.NEW_STRING:#x}\nmov x24,x0\n'+b.textptr('FXBuyText1125','x24')
  # Amount bank units = 100 modern, scaled by the same nominal era wage factor.
  code+='cmp w20,#997\nb.eq wallet_buy1125_'+str(n)+'\ncmp w20,#998\nb.eq wallet_sell1125_'+str(n)+'\nb wallet_show1125_'+str(n)+'\nwallet_buy1125_'+str(n)+':\nucvtf d1,w28\n'+bits('x9',.1)+'fmov d2,x9\nfmul d1,d1,d2\nldr d0,[x27,#0x10]\nfcmp d0,d1\nb.lt wallet_no_funds1125\nstr d1,[sp,#88]\nldr d2,[sp,#80]\nfmul d0,d1,d2\n'+bits('x9',98.)+'fmov d3,x9\nfmul d0,d0,d3\nfcvtzs x9,d0\nadd x9,x9,x19\nmovz x10,#0x9400\nmovk x10,#0x7735,lsl #16\ncmp x9,x10\nb.hi wallet_limit1125\nmov w19,w9\nldr d0,[sp,#88]\nfneg d0,d0\nmov x0,x27\nmov x1,xzr\nbl 0x2a6eb5c\nmov w24,w19\n'+b.put('FXWallet1125_'+str(n))+b.text('FXStatus1125','You exchanged bank money for local travel cash. A 2% exchange fee was deducted. The travel wallet is saved with this life.')+'b wallet_journal1125_'+str(n)+'\nwallet_sell1125_'+str(n)+':\ncbz w19,wallet_show1125_'+str(n)+'\nucvtf d0,w19\nldr d2,[sp,#80]\nfdiv d0,d0,d2\n'+bits('x9',.0098)+'fmov d3,x9\nfmul d0,d0,d3\nmov x0,x27\nmov x1,xzr\nbl 0x2a6eb5c\n'+b.set('FXWallet1125_'+str(n),0)+'mov w19,#0\n'+b.text('FXStatus1125','You sold this currency’s travel cash back to your game bank at the current game rate, less the 2% fee.')+'wallet_journal1125_'+str(n)+':\n'+b.string('I exchanged travel money at the exchange desk and paid its fee.')+f'bl {b.journal55:#x}\nwallet_show1125_{n}:\nmov w9,#100\nudiv w3,w19,w9\nmsub w4,w3,w9,w19\nadd x0,sp,#128\nmov w1,#96\nadr x2,{b.literal(iso+" %u.%02u"):#x}\nbl {b.snprintf:#x}\nadd x0,sp,#128\nbl {h.NEW_STRING:#x}\nmov x28,x0\n'+b.textptr('FXBalance1125','x28')+b.textptr('FXWalletText1125_'+str(n),'x28')+'b finish\nwallet_next1125_'+str(n)+':\n'
 code+='b finish\nwallet_no_funds1125:\n'+b.text('FXStatus1125','You do not have enough bank money for this exchange. Your balances were kept.')+'b finish\nwallet_limit1125:\n'+b.text('FXStatus1125','This travel wallet is full. Your bank money was kept.')+'b finish'
 wallet=b.routine('school1125_exchange_wallet',code)
 r=b.resolved('life_rework_native_action');s=r['source'];head=h.save()+'\n'
 extra=f'cmp w0,#996\nb.lt previous_finance1125\ncmp w0,#999\nb.gt previous_finance1125\nmov w19,w0\nbl {report:#x}\nmov w0,w19\nbl {wallet:#x}\nb finish\nprevious_finance1125:\n'
 b.redirect(r['name'],head+extra+s[len(head):])
 # Close the conspicuous repeatable nineteenth-century bounty windfall. Keep
 # stored active contract amounts and all existing savings/owned jobs intact.
 r=b.resolved('era1121_bounty_contract');s=r['source'];assert s.count('mov w9,#20000')==1;b.redirect(r['name'],s.replace('mov w9,#20000','mov w9,#5000',1))
