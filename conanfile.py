from conans import ConanFile, CMake, tools
from pathlib import Path
import os

# conan create . -e CONAN_SYSREQUIRES_MODE=enabled

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
        #self.run("git clone https://github.com/liballeg/allegro5.git --depth=1 --single-branch --branch=5.2.7")
        self.run("git clone https://github.com/liballeg/allegro5.git --depth=1 --single-branch --branch=master")

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
        flags = "-Wno-dev"
        flags += " -DSHARED=" + str(self.options.shared).lower()
        flags += " -DWANT_DOCS=false"
        flags += " -DWANT_DOCS_HTML=false"
        flags += " -DWANT_EXAMPLES=false"
        flags += " -DWANT_FONT=true"
        flags += " -DWANT_MONOLITH=true"
        flags += " -DWANT_TESTS=false"
        flags += " -DWANT_DEMO=false"
        flags += " -DWANT_RELEASE_LOGGING=false"

        if self.settings.compiler == "Visual Studio" or self.settings.compiler == "clang":
            flags += " -DWANT_STATIC_RUNTIME=" + str(self.settings.compiler.runtime == "MT").lower()
            flags += " -DPREFER_STATIC_DEPS=true"
        else:
            flags += " -DWANT_STATIC_RUNTIME=false"
            flags += " -DPREFER_STATIC_DEPS=false"

        # libpng dependency
        print(self.build_folder)
        tools.replace_in_file(str(os.path.join(self.source_folder, "allegro5/addons/image/CMakeLists.txt")), 
            "find_package(PNG)",
            '''set(PNG_FOUND 1)
               set(HAVE_PNG 1)
               set(PNG_LIBRARIES 1)
               set(PNG_DEFINITIONS 1)
               message(Libraries:)
               message(${{PNG_LIBRARIES})
               message(-- Using PNG from conan package)
               set(PNG_INCLUDE_DIR 1)''')

        #flags += " -DPNG_LIBRARY={}/lib/libpng16.{}".format(libpng_package_folder, lib_suffix)
        #flags += " -DPNG_LIBRARIES={}/lib/libpng16.{}".format(libpng_package_folder, lib_suffix)

        #flags += " -DPNG_PNG_INCLUDE_DIR={}/include/".format(libpng_package_folder)
#
        #flags += " -DJPEG_INCLUDE_DIR={}/include/".format(libjpeg.package_folder)
        #flags += " -DJPEG_LIBRARY={}/lib/libjpeg.{}".format(libjpeg.package_folder, lib_suffix)
#
        #flags += " -DZLIB_INCLUDE_DIR={}/include/".format(zlib_package_folder)
        #flags += " -DZLIB_LIBRARIES={}/lib/zlib.{}".format(zlib_package_folder, lib_suffix)
        #flags += " -DZLIB_LIBRARY={}/lib/zlib.{}".format(zlib_package_folder, lib_suffix)
#
        #flags += " -DWEBP_INCLUDE_DIRS={}/include/".format(libwebp.package_folder)
        #path = libwebp.package_folder
        #front = lib_prefix
        #end = lib_suffix
        #flags += " -DWEBP_LIBRARIES={}/lib/{}webp.{};{}/lib/{}webpdecoder.{};{}/lib/{}webpdemux.{};{}/lib/{}webpmux.{}".format(
        #    path, front, end, path, front, end, path, front, end, path, front, end)
    #
        #flags += " -DFREETYPE_INCLUDE_DIRS={}/include/".format(freetype.package_folder)
        #flags += " -DFREETYPE_LIBRARY={}/lib/freetype.lib;".format(freetype.package_folder)
        #flags += " -DBZIP2_INCLUDE_DIR={}/include/".format(bzip2_package_folder)
        #flags += " -DBZIP2_LIBRARIES={}/lib/bz2.{};".format(bzip2_package_folder, lib_suffix)
#
        #flags += " -DFREETYPE_PNG=on"
        #flags += " -DFREETYPE_BZIP2=on"
        #flags += " -DFREETYPE_ZLIB=on"
#
        #flags += " -DFLAC_INCLUDE_DIR={}/include/".format(flac.package_folder)
        #flags += " -DFLAC_LIBRARY={}/lib/FLAC.{};{}/lib/FLAC++.{}".format(flac.package_folder, lib_suffix, flac.package_folder, lib_suffix)
        #flags += " -DOGG_INCLUDE_DIR={}/include/".format(ogg.package_folder)
        #flags += " -DOGG_LIBRARY={}/lib/ogg.{}".format(ogg.package_folder, lib_suffix)

        # Call cmake generate
        path = Path(self.build_folder + "/allegro5/build")
        path.mkdir(parents=True, exist_ok=True)
        os.chdir(path)
        self.run("cmake .. " + flags)

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

