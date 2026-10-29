import {bundle} from '@remotion/bundler';
import {getCompositions,renderMedia,renderStill,openBrowser} from '@remotion/renderer';
import {mkdir} from 'node:fs/promises';
import path from 'node:path';
const out=path.resolve('../renders');
await mkdir(out,{recursive:true});
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),onProgress:()=>{}});
const browser=await openBrowser('chrome');
const comps=await getCompositions(serveUrl,{puppeteerInstance:browser});
for (const comp of comps){
 console.log('Rendering '+comp.id);
 await renderStill({serveUrl,composition:comp,output:path.join(out,comp.id+'.png'),frame:comp.id==='Demo'?850:65,puppeteerInstance:browser});
 await renderMedia({serveUrl,composition:comp,outputLocation:path.join(out,comp.id+'.mp4'),codec:'h264',crf:20,concurrency:4,puppeteerInstance:browser,logLevel:'error'});
 console.log('Done '+comp.id);
}
await browser.close({silent:true});
