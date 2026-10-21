"""Verify and register a portable project, preserving all existing CapCut drafts."""
import argparse
import csv
import io
import os
import shutil
import subprocess
import tempfile
import time
import uuid
from pathlib import Path
from portable_common import *

def assert_closed():
    if os.name != 'nt': raise SystemExit('This installer supports Windows only.')
    result = subprocess.run(['tasklist','/FO','CSV','/NH'],capture_output=True,text=True,errors='replace',check=True)
    names = {row[0].casefold() for row in csv.reader(io.StringIO(result.stdout)) if row}
    if 'capcut.exe' in names:
        raise SystemExit('CapCut is running. Save your work, close CapCut, and retry.')

def safe_rel(value):
    rel=Path(value)
    if rel.is_absolute() or '..' in rel.parts or ':' in value or '\\' in value:
        raise SystemExit('Unsafe manifest path: '+value)
    return rel

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--package',default=str(Path(__file__).parent))
    ap.add_argument('--draft-root')
    ap.add_argument('--name')
    ap.add_argument('--verify-only',action='store_true')
    args=ap.parse_args()
    package=Path(args.package).resolve(); manifest=read(package/'manifest.json')
    records=manifest['files']
    for r in records:
        file=package/safe_rel(r['path'])
        if not file.is_file() or file.stat().st_size!=r['size'] or digest(file)!=r['sha256']:
            raise SystemExit('Missing/corrupt package file: '+r['path'])
    if args.verify_only:
        print('Package hashes verified:',len(records));return
    assert_closed()
    root=Path(args.draft_root).expanduser().resolve() if args.draft_root else Path(os.environ['LOCALAPPDATA'])/'CapCut/User Data/Projects/com.lveditor.draft'
    if not root.is_dir():raise SystemExit('CapCut draft root not found. Start CapCut once, close it, or specify --draft-root.')
    index_file=root/'root_meta_info.json'
    if not index_file.is_file():raise SystemExit('Existing root_meta_info.json required; no index was modified.')
    baseline=digest(index_file); index=read(index_file)
    if not isinstance(index.get('all_draft_store'),list) or not isinstance(index.get('draft_ids'),int):
        raise SystemExit('Unsupported CapCut index format. No changes made.')
    base=args.name or manifest['project_name']+'_공유본'
    if not base or base in ('.','..') or any(c in base for c in '/\\:*?"<>|') or base.endswith(('.', ' ')):
        raise SystemExit('Invalid project name.')
    existing={e.get('draft_name') for e in index['all_draft_store']}
    name=base;n=2
    while (root/name).exists() or name in existing:
        name=base+f'_{n}';n+=1
    destination=root/name
    stage=Path(tempfile.mkdtemp(prefix='.jieum_install_',dir=root))
    published=False
    try:
        shutil.copytree(package/'Project',stage,dirs_exist_ok=True)
        def rebase(s):
            if s==PLACEHOLDER:return destination.as_posix()
            rel=relative_placeholder(s)
            if rel is None:raise ValueError('Unexpected external path in package: '+s)
            return (destination/rel).as_posix()
        for f in stage.rglob('*.json'):
            data=transform(read(f),rebase)
            # This sentinel is deliberately not a filesystem path.
            def root_token(v):
                if isinstance(v,dict):return {k:root_token(x) for k,x in v.items()}
                if isinstance(v,list):return [root_token(x) for x in v]
                return root.as_posix() if v=='__CAPCUT_DRAFT_ROOT__' else v
            write(f,root_token(data))
        meta_file=stage/'draft_meta_info.json';meta=read(meta_file)
        new_id=str(uuid.uuid4()).upper()
        meta.update(draft_id=new_id,draft_name=name,draft_fold_path=destination.as_posix(),draft_root_path=root.as_posix(),draft_cover='draft_cover.jpg',tm_draft_removed=0)
        write(meta_file,meta)
        for f in stage.rglob('*.json'):
            for s in paths(read(f)):
                p=Path(s)
                if norm(s)==norm(root):continue
                if not p.is_relative_to(destination) or not (stage/p.relative_to(destination)).exists():
                    raise ValueError('Unresolved installed path: '+s)
        content=read(stage/'draft_content.json')
        timeline=read(stage/'Timelines/project.json')
        if timeline['main_timeline_id']!=content['id']:raise ValueError('Timeline identity mismatch')
        if read(stage/'Timelines'/content['id']/'draft_content.json')!=content:raise ValueError('Timeline content mismatch')
        entry={k:v for k,v in meta.items() if k not in ('draft_materials','draft_materials_copied_info','draft_segment_extra_info')}
        entry.update(draft_json_file=(destination/'draft_content.json').as_posix(),draft_cover=(destination/'draft_cover.jpg').as_posix(),draft_timeline_materials_size=sum(f.stat().st_size for f in stage.rglob('*') if f.is_file()),tm_duration=content['duration'])
        # Preserve the monotonic local counter; it is not necessarily the list length.
        index['draft_ids']=max(index['draft_ids'],len(index['all_draft_store']))+1
        index['all_draft_store'].insert(0,entry)
        temp_index=root/('.root_meta_info.'+uuid.uuid4().hex+'.tmp')
        write(temp_index,index)
        try:
            assert_closed()
            if digest(index_file)!=baseline:raise RuntimeError('CapCut index changed during installation. Retry after closing CapCut.')
            backup=root/('root_meta_info.before_jieum_'+time.strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:8]+'.json')
            shutil.copy2(index_file,backup)
            stage.rename(destination);published=True
            assert_closed()
            if digest(index_file)!=baseline:raise RuntimeError('CapCut index changed; project copied but was not registered.')
            os.replace(temp_index,index_file)
        finally:
            if temp_index.exists():temp_index.unlink()
        print(json.dumps({'installed_project':str(destination),'draft_id':new_id,'duration_seconds':content['duration']/1e6,'existing_projects_preserved':True,'index_backup':str(backup)},ensure_ascii=False,indent=2))
    finally:
        if not published and stage.exists():shutil.rmtree(stage)

if __name__=='__main__':main()
