import os
import tempfile
import shutil
import fastaq

class Error (Exception): pass


class Runner:
    def __init__(
      self,
      ref,
      query,
      outfile,
      min_id=None,
      min_length=None,
      breaklen=None,
      coords_header=True,
      maxmatch=False
   ):
        self.qry = query
        self.ref = ref
        self.outfile = outfile
        self.min_id = min_id
        self.min_length = min_length
        self.breaklen = breaklen
        self.coords_header = coords_header
        self.maxmatch = maxmatch
    


    def _nucmer_command(self, ref, qry, outprefix):
        command = 'nucmer -p ' + outprefix

        if self.breaklen is not None:
            command += ' -b ' + str(self.breaklen)

        if self.maxmatch:
            command += ' --maxmatch'

        return command + ' ' + ref + ' ' + qry



    def _delta_filter_command(self, infile, outfile):
        command = 'delta-filter'

        if self.min_id is not None:
            command += ' -i ' + str(self.min_id)

        if self.min_length is not None:
            command += ' -l ' + str(self.min_length)

        return command + ' ' + infile + ' > ' + outfile
        

    def _show_coords_command(self, infile, outfile):
        command = 'show-coords -dTlro'

        if not self.coords_header:
            command += ' -H'

        return command + ' ' + infile + ' > ' + outfile


    def _write_script(self, script_name, ref, qry, outfile):
        f = fastaq.utils.open_file_write(script_name)
        print(self._nucmer_command(ref, qry, 'p'), file=f)
        print(self._delta_filter_command('p.delta', 'p.delta.filter'), file=f)
        print(self._show_coords_command('p.delta.filter', outfile), file=f)
        fastaq.utils.close(f)
    

    def run(self):
        qry = os.path.abspath(self.qry)
        ref = os.path.abspath(self.ref)
        outfile = os.path.abspath(self.outfile)
        tmpdir = tempfile.mkdtemp(prefix='tmp.run_nucmer.', dir=os.getcwd())
        original_dir = os.getcwd()
        os.chdir(tmpdir)
        script = 'run_nucmer.sh'
        self._write_script(script, ref, qry, outfile) 
        fastaq.utils.syscall('bash ' + script)
        os.chdir(original_dir)
        shutil.rmtree(tmpdir)
