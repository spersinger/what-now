from pythonforandroid.toolchain import Recipe, shprint, current_directory
from pythonforandroid.logger import info
import sh


class PortAudioRecipe(Recipe):

    version = '19.7.0'
    url = 'https://github.com/PortAudio/portaudio/archive/refs/tags/v{version}.tar.gz'
    
    patches = ['configure.patch']

    def build_arch(self, arch):
        super().build_arch(arch)
        env = self.get_recipe_env(arch)
        
        with current_directory(self.get_build_dir(arch.arch)):
            shprint(sh.Command("./configure"), '--host=' + arch.command_prefix, _env=env)
            shprint(sh.Command("make"), _env=env)

recipe = PortAudioRecipe()