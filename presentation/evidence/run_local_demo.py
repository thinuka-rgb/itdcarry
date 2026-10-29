import sys, json, subprocess, hashlib, time, shutil
from pathlib import Path
from datetime import datetime, timezone

root = Path(__file__).parent / 'itdcarry'
sys.path.insert(0, str(root))
from backend.domain import ITD, RunStatus
from backend.exact_match import any_exact_recovery, local_verdict
from pipeline.parse_getitd import parse_high_confidence_itds

out = Path(__file__).parent / 'local-evidence'
out.mkdir(exist_ok=True)
manifest = json.loads((root/'data/synthetic_case/generated/manifest.json').read_text())
expected = ITD(manifest['itd_position'], manifest['itd_length_bp'], manifest['itd_sequence'])
results = {'mode':'Local core execution; no Daytona or Neo4j execution', 'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(), 'executed_at_utc':datetime.now(timezone.utc).isoformat(), 'marker':manifest, 'runs':[]}
for name in ['compatible','changed']:
    profile = json.loads((root/f'pipeline/profiles/{name}.json').read_text())
    sample = 'pitch-'+name
    args = [sys.executable,'vendor/getitd/getitd.py','-reference','vendor/getitd/anno/amplicon.txt','-anno','vendor/getitd/anno/amplicon_kayser.tsv',*profile['getitd_args'],sample,'data/synthetic_case/generated/FLT3-ITD-DEMO-001_R1.fastq','data/synthetic_case/generated/FLT3-ITD-DEMO-001_R2.fastq']
    start=time.monotonic()
    run=subprocess.run(args,cwd=root,text=True,capture_output=True)
    (out/f'{name}-stdout.txt').write_text(run.stdout,encoding='utf-8')
    (out/f'{name}-stderr.txt').write_text(run.stderr,encoding='utf-8')
    tsv = root/f'{sample}_getitd/itds_collapsed-is-same_is-similar_is-close_is-same_trailing_hc.tsv'
    calls = parse_high_confidence_itds(tsv) if run.returncode==0 else []
    recovered = any_exact_recovery(expected,[c.marker for c in calls]) if run.returncode==0 else None
    result={'profile':name,'command':args[1:],'exit_code':run.returncode,'duration_seconds':round(time.monotonic()-start,3),'exact_recovery':recovered,'high_confidence_tsv_exists':tsv.exists(),'reference_verdict':str(local_verdict(RunStatus.COMPLETED if run.returncode==0 else RunStatus.FAILED,recovered)), 'calls':[{'position':c.marker.position,'length_bp':c.marker.length_bp,'sequence':c.marker.sequence,'unique_supporting_reads':c.unique_supporting_reads,'total_supporting_reads':c.total_supporting_reads} for c in calls]}
    if tsv.exists(): shutil.copy2(tsv,out/f'{name}-raw-output.tsv')
    results['runs'].append(result)
    print(json.dumps(result),flush=True)
    if run.returncode: print(run.stderr[-3000:],flush=True)
for key,filename in [('r1_sha256','FLT3-ITD-DEMO-001_R1.fastq'),('r2_sha256','FLT3-ITD-DEMO-001_R2.fastq')]:
    actual=hashlib.sha256((root/'data/synthetic_case/generated'/filename).read_bytes()).hexdigest()
    results[key+'_verified']=actual==manifest[key]
(out/'results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
