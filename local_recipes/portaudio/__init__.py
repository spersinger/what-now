# pythonforandroid/recipes/portaudio/__init__.py
from pythonforandroid.recipe import NDKRecipe
from pythonforandroid.util import current_directory
from pythonforandroid.logger import shprint
from os.path import join, exists
import sh


class PortAudioRecipe(NDKRecipe):
    """
    PortAudio v19 built as a static library for Android.
    Uses OpenSL ES backend available on all Android API >= 14.
    """
    version = "19.7.0"
    url = "https://github.com/PortAudio/portaudio/archive/refs/tags/v{version}.tar.gz"
    site_packages_name = "portaudio"
    name = "portaudio"

    generated_libraries = ["libportaudio.so"]
    patches = ["configure.patch"]
    
    def should_build(self, arch):
        return not exists(join(self.get_build_dir(arch.arch), "lib", "libportaudio.so"))
    
    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        # add OpenSL ES include path
        ndk = self.ctx.ndk_dir
        sysroot = join(ndk, "toolchains", "llvm", "prebuilt",
                       "linux-x86_64", "sysroot")
        env["CFLAGS"] += f" -I{join(sysroot, 'usr', 'include')}"
        env["LDFLAGS"] += " -lOpenSLES -llog"
        return env

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        build_dir = self.get_build_dir(arch.arch)

        with current_directory(build_dir):
            # configure for android: disable ALSA/JACK, enable openSLES
            shprint(
                sh.Command("./configure"),
                f"--host={arch.command_prefix}",
                "--enable-static",
                "--disable-shared",
                "--with-opensles",
                "--without-jack",
                "--without-alsa",
                "--without-asihpi",
                "--without-winapi",
                # f"CC={env['CFLAGS']}",
                # f"LDFLAGS={env['LDFLAGS']}",
                _env=env
            )
            
            shprint(
                sh.make,
                _env=env
            )


recipe = PortAudioRecipe()