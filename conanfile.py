from conans import ConanFile, CMake, tools
from pathlib import Path
import os

class Allegro5Conan(ConanFile):
    name = "allegro5"
    version = "5.2.7"
    license = "<Put the package license here>"
    author = "<Put your name here> <And your email here>"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of Allegro5 here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"

    # Fixed dependencies
    requires = "libpng/1.6.37", \
                "zlib/1.2.11", \
                "bzip2/1.0.8", \
                "libjpeg/9d", \
                "freetype/2.11.1", \
                "libwebp/1.2.2", \
                "flac/1.3.3", \
                "ogg/1.3.5"

    def requirements(self):       # Conditional dependencies
        if self.settings.os != "Windows":
            self.requires("xorg/system")
            package_tool = tools.SystemPackageTool(conanfile=self, default_mode='verify')
            package_tool.install(update=True, packages="libgl1-mesa-dev")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        self.run("git clone https://github.com/liballeg/allegro5.git --depth=1 --single-branch --branch=5.2.7")

    def generate(self):

        zlib = self.dependencies["zlib"]
        libpng = self.dependencies["libpng"]
        bzip2 = self.dependencies["bzip2"]

        libjpeg = self.dependencies["libjpeg"]
        freetype = self.dependencies["freetype"]
        libwebp = self.dependencies["libwebp"]
        flac = self.dependencies["flac"]
        ogg = self.dependencies["ogg"]

        # Read paths into variables because they are read-only
        zlib_package_folder = zlib.package_folder
        libpng_package_folder = libpng.package_folder
        bzip2_package_folder = bzip2.package_folder

        # Library paths cannot contain windows backspaces because of cmake's target_link_libraries()
        if self.settings.os == "Windows":
            zlib_package_folder = zlib_package_folder.replace("\\","/")
            libpng_package_folder = libpng_package_folder.replace("\\","/")
            bzip2_package_folder = bzip2_package_folder.replace("\\","/")

        # Configure dependency flags for cmake
        flags = ""
        flags += " -DPREFER_STATIC_DEPS=true"
        flags += " -DSHARED=" + str(self.options.shared).lower()
        flags += " -DWANT_DOCS=false"
        flags += " -DWANT_DOCS_HTML=false"
        flags += " -DWANT_EXAMPLES=false"
        flags += " -DWANT_FONT=true"
        flags += " -DWANT_MONOLITH=true"
        flags += " -DWANT_TESTS=false"
        flags += " -DWANT_DEMO=false"
        flags += " -DWANT_RELEASE_LOGGING=false"
        
        if self.settings.os == "Windows":
            flags += " -DWANT_STATIC_RUNTIME=" + str(self.settings.compiler.runtime == "MT").lower()
        else:
            flags += " -DWANT_STATIC_RUNTIME=false"

        flags += " -DPNG_PNG_INCLUDE_DIR=" + libpng_package_folder + "/include/"
        flags += " -DPNG_LIBRARY=" + libpng_package_folder + "/lib/libpng16.lib;"
        flags += " -DPNG_LIBRARIES=" + libpng_package_folder + "/lib/libpng16.lib;"

        flags += " -DJPEG_INCLUDE_DIR=" + libjpeg.package_folder + "/include/"
        flags += " -DJPEG_LIBRARY=" + libjpeg.package_folder + "/lib/libjpeg.lib;"

        flags += " -DZLIB_INCLUDE_DIR=" + zlib_package_folder + "/include/"
        flags += " -DZLIB_LIBRARIES=" + zlib_package_folder + "/lib/zlib.lib"
        flags += " -DZLIB_LIBRARY=" + zlib_package_folder + "/lib/zlib.lib"

        flags += " -DWEBP_INCLUDE_DIRS=" + libwebp.package_folder + "/include/"
        flags += " -DWEBP_LIBRARIES=" + libwebp.package_folder + "/lib/webp.lib;" + \
            libwebp.package_folder + "/lib/webpdecoder.lib;" + \
            libwebp.package_folder + "/lib/webpdemux.lib;" + \
            libwebp.package_folder + "/lib/webpmux.lib"
        
        flags += " -DFREETYPE_INCLUDE_DIRS=" + freetype.package_folder + "/include/"
        flags += " -DFREETYPE_LIBRARY=" + freetype.package_folder + "/lib/freetype.lib;"
        flags += " -DBZIP2_INCLUDE_DIR=" + bzip2_package_folder + "/include/"
        flags += " -DBZIP2_LIBRARIES=" + bzip2_package_folder + "/lib/bz2.lib;"

        flags += " -DFREETYPE_PNG=on"
        flags += " -DFREETYPE_BZIP2=on"
        flags += " -DFREETYPE_ZLIB=on"

        flags += " -DFLAC_INCLUDE_DIR=" + flac.package_folder + "/include/"
        flags += " -DFLAC_LIBRARY=" + flac.package_folder + "/lib/FLAC.lib;" + flac.package_folder + "/lib/FLAC++.lib;"
        flags += " -DOGG_INCLUDE_DIR=" + ogg.package_folder + "/include/"
        flags += " -DOGG_LIBRARY=" + ogg.package_folder + "/lib/ogg.lib;"

        # Call cmake generate
        path = Path(self.build_folder + "/allegro5/build")
        path.mkdir(parents=True, exist_ok=True)
        os.chdir(path)
        
        if self.settings.os == "Windows":
            self.run("cmake .. -Wno-dev" + flags)
        else:
            self.run("cmake .. -Wno-dev")

    def build(self):
        if self.settings.os == "Windows":
            self.run("cd allegro5/build & cmake --build . --config RelWithDebInfo") # Build the project
        else:
            path = Path(self.build_folder + "/allegro5/build")
            path.mkdir(parents=True, exist_ok=True)
            os.chdir(path)
            self.run("make") # Build the project

    def package(self):
        self.copy("*", dst="include", src="allegro5/include")
        self.copy("*.lib", dst="lib", src="allegro5/build/lib/RelWithDebInfo")

    def package_info(self):
        self.cpp_info.libs = ["allegro_monolith-static"]

