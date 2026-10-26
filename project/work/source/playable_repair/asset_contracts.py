"""Verify final serialized resource references by file identity, not path ID alone."""
from collections import Counter
from pathlib import PurePosixPath
import hashlib
import UnityPy


def verify_resources(pack, data, imported):
    env = UnityPy.load(pack)
    outer = UnityPy.load(data)
    files = {o.assets_file.name:o.assets_file for o in env.objects}
    files.update({o.assets_file.name:o.assets_file for o in outer.objects})
    manager = next(o for o in outer.objects if o.type.name == 'ResourceManager')
    paths = manager.read_typetree()['m_Container']
    counts = Counter(name for name,_ in paths)
    aliases = dict(paths)

    def resolve(owner, ptr):
        file_id, path_id = ptr['m_FileID'], ptr['m_PathID']
        target = owner
        if file_id:
            assert 1 <= file_id <= len(owner.externals), ptr
            name = PurePosixPath(owner.externals[file_id-1].path).name
            assert name in files, ('missing external file', name)
            target = files[name]
        assert path_id in target.objects, ('missing object', target.name,path_id)
        return target.objects[path_id]

    checked=[]
    for row in imported:
        name=row['resource'];assert counts[name] == 1, ('duplicate resource',name)
        sprite=resolve(manager.assets_file, aliases[name])
        assert sprite.type.name == 'Sprite', (name,sprite.type.name)
        tree=sprite.read_typetree();texture=resolve(sprite.assets_file,tree['m_RD']['texture'])
        assert texture.type.name == 'Texture2D'
        assert tree['m_SpriteAtlas']['m_PathID'] == 0, ('stale sprite atlas',name)
        im=texture.read().image.convert('RGBA')
        assert list(im.size)==row['canvas'],(name,im.size,row['canvas'])
        assert hashlib.sha256(im.tobytes()).hexdigest()==row['pixel_sha256'],name
        rect=tree['m_Rect'];tr=tree['m_RD']['textureRect']
        assert [rect['width'],rect['height']]==[float(im.width),float(im.height)]
        assert [tr['width'],tr['height']]==[float(im.width),float(im.height)]
        vertices=tree['m_RD']['m_VertexData'];assert vertices['m_VertexCount']==4,name
        assert vertices['m_Channels'][0]['dimension']==3,name
        assert vertices['m_Channels'][4]['dimension']==2,name
        assert len(tree['m_RD']['m_IndexBuffer'])==12,name
        assert im.getbbox(),('fully transparent resource',name)
        checked.append(dict(resource=name,sprite_file=sprite.assets_file.name,
                            texture_file=texture.assets_file.name,
                            sprite_id=sprite.path_id,texture_id=texture.path_id))
    return dict(passed=True,resources=len(checked),file_identity_checked=True,
                generic_type='Sprite',texture_type='Texture2D',checked=checked,
                GPU_rendering_tested=False)
