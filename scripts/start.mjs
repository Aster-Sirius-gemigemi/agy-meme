import {spawn} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const script = fileURLToPath(new URL('./server.py', import.meta.url));
const runtimes = process.platform === 'win32' ? [['py','-3'],['python']] : [['python3']];
function launch(index) {
  const [command, ...flags] = runtimes[index];
  const child = spawn(command,[...flags,'-B','-X','utf8',script],{stdio:'inherit',windowsHide:true});
  child.once('error',error=>{
    if(error.code==='ENOENT' && index+1<runtimes.length) launch(index+1);
    else {console.error(error.message);process.exitCode=1;}
  });
  child.once('exit',code=>{process.exitCode=code??1;});
  process.once('SIGTERM',()=>child.kill());
}
launch(0);
