# pythonforandroid/recipes/pyaudio/__init__.py
from pythonforandroid.recipe import CythonRecipe, Recipe
from pythonforandroid.util import current_directory
from pythonforandroid.logger import shprint
from os.path import join
import sh


# changed from CythonRecipe
class PyAudioRecipe(CythonRecipe):
    """
    PyAudio recipe with PortAudio built for Android.
    Depends on the portaudio recipe.
    """
    version = "0.2.14"
    url = "https://files.pythonhosted.org/packages/source/P/PyAudio/PyAudio-{version}.tar.gz"
    site_packages_name = "pyaudio"
    name = "pyaudio"

    depends = ["portaudio", "setuptools"]
    patches = ["setup.patch"]

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        
        portaudio = Recipe.get_recipe("portaudio", self.ctx)
        portaudio_dir = portaudio.get_build_dir(arch.arch)
        
        ndk_sysroot = join(
            self.ctx.ndk_dir,
            "toolchains", "llvm", "prebuilt", "linux-x86_64", "sysroot"
        )
        
        env["CFLAGS"] += f" -I{join(portaudio_dir, 'include')}"
        env["CFLAGS"] += f" -I{join(ndk_sysroot, 'usr', 'include')}"
        env["CFLAGS"] += f" -I{join(ndk_sysroot, 'usr', 'include', 'aarch64-linux-android')}"
        env["LDFLAGS"] += f" -L{join(portaudio_dir, 'lib', '.libs')} -lportaudio"
        
        return env


recipe = PyAudioRecipe()