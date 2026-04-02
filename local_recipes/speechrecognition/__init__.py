from pythonforandroid.toolchain import Recipe #, shprint, current_directory
from pythonforandroid.recipe import PythonRecipe
from os.path import exists, join
#import sh
#import glob

'''
dependencies:
- python 3.9+
- pyaudio 0.2.11+
'''


class SpeechRecognitionRecipe(PythonRecipe):

    version = '3.15.1'
    url = 'https://files.pythonhosted.org/packages/49/70/30b861a00aab91433dadcf827a0420319d71e319decdeb2f721d217c3db3/speechrecognition-{version}.tar.gz'

    depends = ['pyaudio']

    # seemingly generally the most important part for most recipes
    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        
        # dependency recipe includes: two types
        # either [name]_inc_dir and [name]_lib_dir same
        #   -> `name_inc_dir = name_lib_dir = name.get_build_dir(arch.arch)`
        # or they're different
        #   -> `name_lib_dir = join(name.get_build_dir(arch.arch), '[lib_dirname]', '.libs')`
        #   -> `name_inc_dir = join(name.get_build_dir(arch.arch), 'include')`
        # last part: adjust current recipe env
        #   -> `env["NAME_ROOT"] = "{}:{}".format(name_lib_dir, name_inc_dir)`
        
        # pyaudio dependency
        pyaudio = self.get_recipe('pyaudio', self.ctx)
        pyaudio_inc_dir = join(pyaudio.get_build_dir(arch.arch), 'include')
        pyaudio_lib_dir = join(pyaudio.get_build_dir(arch.arch), 'lib', '.libs')
        env["PYAUDIO_ROOT"] = "{}:{}".format(pyaudio_lib_dir, pyaudio_inc_dir)
        
        return env

    # def build_arch(self, arch):
    #     super().build_arch(self)
    #     # Build the code. Make sure to use the right build dir, e.g.
    #     with current_directory(self.get_build_dir(arch.arch)):
    #         sh.Command("python -m pip install .") # (this is just about the default command)


recipe = SpeechRecognitionRecipe()