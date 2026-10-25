"""Calendar gates on stock random invitations, alongside the existing menu gates."""
from native_hooks import h


def hooks(b):
    # Audited GetEligibleSocialMediaChannel builds a candidate list and then
    # selects an enum. Skip each candidate BEFORE it is added. Resumes reload
    # the Game singleton; they do not consume the DataHub pointer in x8.
    year=b.old['v45_current_year']['stub']
    candidates=[('facebook',2004,0x2650790,0x2650830,1),('instagram',2010,0x2650870,0x2650910,2),('twitter',2006,0x2650950,0x26509f0,3),('tiktok',2018,0x2650a30,0x2650ad0,4),('twitch',2011,0x2650b10,0x2650bb0,6),('onlyfans',2016,0x2650bf0,0x2650c90,7),('youtube',2005,0x2650d7c,0x2650cb8,5)]
    for name,start,site,resume,channel in candidates:
        assert bytes(b.blob[b.off(site):b.off(site)+4])==h.asm(f'mov w0,#{channel}',site)
        b.install('followup_random_invitation_'+name,site,
                  f'bl {year:#x}\ncmp w0,#{start}\nb.lt return_custom\nb finish',custom_resume=resume)
