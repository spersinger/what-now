from pythonforandroid.toolchain import Recipe, shprint, current_directory
from pythonforandroid.recipe import PythonRecipe
from pythonforandroid.logger import info
from os.path import exists, join
import sh

'''
dependencies:
# - portaudiov19
'''


class PyAudioRecipe(Recipe):

    version = '0.2.14'
    url = 'https://files.pythonhosted.org/packages/26/1d/8878c7752febb0f6716a7e1a52cb92ac98871c5aa522cba181878091607c/PyAudio-{version}.tar.gz'

    depends = ['portaudio']
    

    def get_recipe_env(self, arch): 
        env = super().get_recipe_env(arch)
        
        # portaudio dependency
        portaudio_build_dir = self.get_recipe('portaudio', self.ctx).get_build_dir(arch.arch)
        
        # setuptools (necessary?)
        setuptools_build_dir = self.get_recipe('setuptools', self.ctx).get_build_dir(arch.arch)      

        env["CFLAGS"] = f"-I{portaudio_build_dir}/include"
        env["LDFLAGS"] = f"-L{portaudio_build_dir}/lib -L{setuptools_build_dir}/build/lib"
        
        return env
    
    def build_arch(self, arch):
        env = self.get_recipe_env(arch)

        with current_directory(self.get_build_dir(arch.arch)):
            hostpython = sh.Command(self.ctx.hostpython)
            
            # current bug: __WORDSIZE is somehow 32 instead of 64
            # (pyconfig-32.h not found)
            # (host and target both 64b-ELF)
        
            shprint(
                sh.Command("python"),
                'setup.py',
                'build',
                _env=env
            )
            
            


recipe = PyAudioRecipe()