from conan.tools.microsoft import msvc_runtime_flag
from conans import ConanFile, CMake, tools
import os, shutil

required_conan_version = ">=1.33.0"

class Allegro5Conan(ConanFile):
    name = "allegro5"
    license = ("ZLib", "BSD-3-Clause")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/liballeg/allegro5"
    description = "Cross-platform graphics framework for basic game development and desktop applications"
    topics = ("allegro5", "gamedev", "gui", "framework", "graphics")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "fPIC": [True, False]
    }
    default_options = {
        "fPIC": True
    }
    
    generators = "cmake_find_package", "pkg_config"
    _cmake = None

    def requirements(self):       # Conditional dependencies
        self.requires("freeimage/3.18.0")
        self.requires("freetype/2.11.1")
        self.requires("flac/1.3.3")
        self.requires("ogg/1.3.5")
        self.requires("vorbis/1.3.7")
        self.requires("minimp3/20200304")
        self.requires("openal/1.21.1")
        self.requires("physfs/3.0.2")
        self.requires("opusfile/0.12")
        self.requires("theora/1.1.1")
        self.requires("opengl/system")
        self.requires("pkgconf/1.7.4")

        if self.settings.os == "Linux":
            self.requires("xorg/system")
            self.requires("glu/system")

        if not self.settings.os == "Windows":
            self.requires("gtk/3.24.24")
            self.requires("libalsa/1.2.5.1")
            self.requires("pulseaudio/14.2")
            self.requires("openssl/1.1.1m")
            self.requires("zlib/1.2.12")
            self.requires("expat/2.4.6")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _patch_addon(self, addon, find, replace):
        path = None
        if (addon == None):
            path = os.path.join(self._source_subfolder, "CMakeLists.txt")
        elif (addon == "addons"):
            path = os.path.join(self._source_subfolder, "addons", "CMakeLists.txt")
        else:
            path = os.path.join(self._source_subfolder, "addons", addon, "CMakeLists.txt")
        tools.replace_in_file(path, find, replace)
        
    def _patch_sources(self):
        self.output.info("Patching sources")
        self._patch_addon("acodec", "find_package(FLAC)", "find_package(flac REQUIRED)\nset(FLAC_STATIC 1)\n")
        self._patch_addon("addons", "PHYSFS_LIBRARY", "PHYSFS_LIBRARIES")
        self._patch_addon("acodec", "find_package(Opus)", "find_package(opusfile REQUIRED)")
        self._patch_addon("acodec", "OPUS_INCLUDE_DIR", "opusfile_INCLUDE_DIR")
        self._patch_addon("acodec", "OPUS_LIBRARIES", "opusfile_LIBRARIES")
        self._patch_addon("image", "FREEIMAGE_INCLUDE_PATH", "FREEIMAGE_INCLUDE_DIR")

        self._patch_addon("acodec", "list(APPEND ACODEC_SOURCES mp3.c)", 
            "list(APPEND ACODEC_SOURCES mp3.c)\nlist(APPEND ACODEC_INCLUDE_DIRECTORIES ${MINIMP3_INCLUDE_DIRS})")
            
        # List all dependencies explicitly
        self._patch_addon(None, "link_directories(${MONOLITH_LINK_DIRECTORIES})",
            '''link_directories(${MONOLITH_LINK_DIRECTORIES})\n
               find_package(ZLIB REQUIRED)\n
               find_package(JPEG REQUIRED)\n
               find_package(PNG REQUIRED)\n
               find_package(Ogg REQUIRED)\n
               find_package(OpenSSL REQUIRED)\n
               find_package(Opus REQUIRED)\n
               find_package(Brotli REQUIRED)\n
               find_package(BZip2 REQUIRED)\n
               find_package(WebP REQUIRED)\n
               find_package(OpenEXR REQUIRED)\n
               find_package(JXR REQUIRED)\n
               find_package(libraw REQUIRED)\n
               find_package(TIFF REQUIRED)\n
               find_package(OpenJPEG REQUIRED)''')
               
        # Fix a Microsoft DirectX SDK issue with modern compilers
        path = os.path.join(self._source_subfolder, "src", "win", "whaptic.cpp")
        tools.replace_in_file(path, "#include <initguid.h>", "#define INITGUID\n#include <../shared/guiddef.h>")

        #self._patch_addon(None, "-DALLEGRO_SRC ", "-DALLEGRO_SRC -DFREEIMAGE_LIB ")

        #self._patch_addon(None, "find_package(X11)", "find_package(X11 REQUIRED)\nset(X11_LIBRARIES ${X11_LIBRARIES} xcb dl)")
        #self._patch_addon(None, "set(INSTALL_PKG_CONFIG_FILES true)", "set(INSTALL_PKG_CONFIG_FILES false)")

        #self._patch_addon("addons", "run_c_compile_test(\"${FREETYPE_TEST_SOURCE}\" TTF_COMPILES)", "")
        #self._patch_addon("addons", "run_c_compile_test(\"${FREETYPE_TEST_SOURCE}\" TTF_COMPILES_WITH_EXTRA_DEPS)", 
        #    '''find_package(Brotli REQUIRED)
        #       list(APPEND FREETYPE_STATIC_LIBRARIES "${Brotli_LIBRARIES}")
        #       run_c_compile_test("${FREETYPE_TEST_SOURCE}" TTF_COMPILES_WITH_EXTRA_DEPS)''')
        #self._patch_addon(None, "link_directories(${MONOLITH_LINK_DIRECTORIES})",       # ALSA IS NON-WINDOWS ONLY!!!!!!
        #    '''link_directories(${MONOLITH_LINK_DIRECTORIES})\n
        #       find_package(ZLIB REQUIRED)\n
        #       find_package(Ogg REQUIRED)\n
        #       find_package(OpenSSL REQUIRED)\n
        #       find_package(Opus REQUIRED)\n
        #       find_package(PNG REQUIRED)\n
        #       find_package(BZip2 REQUIRED)\n
        #       find_package(Brotli REQUIRED)\n''')

    def add_find_package_case(self, file_name, name, toNames):
        with open(file_name, 'r') as f:
            content = f.read()
        
        appendix = ""
        
        if not isinstance(toNames, list):
            toNames = [toNames]
            
        for toName in toNames:
            for key in ["FOUND", "INCLUDE_DIR", "INCLUDE_DIRS", "INCLUDES",
                        "DEFINITIONS", "LIBRARIES", "LIBRARIES_TARGETS",
                        "LIBS", "LIBRARY_LIST", "LIB_DIRS"]:
                appendix = appendix + "set(" + toName + "_" + key + " ${" + name + "_" + key + "})\n"
            
        content = content + "\n\n" + appendix
    
        with open(file_name, "w") as handle:
            handle.write(content)
        
        # For case-sensitive file-systems, keep all known casings available
        for toName in toNames:
            try:
                shutil.copy(file_name, os.path.join(os.path.dirname(file_name), "Find" + toName + ".cmake"))
            except:
                pass

    def generate(self):
        self.output.info("Patching Find*.cmake module files")
        self.add_find_package_case("FindFreeImage.cmake", "FreeImage", "FREEIMAGE")
        self.add_find_package_case("FindWebP.cmake", "WebP", "WEBP")
        self.add_find_package_case("FindVorbis.cmake", "Vorbis", "VORBIS")
        self.add_find_package_case("FindOgg.cmake", "Ogg", "OGG")
        self.add_find_package_case("Findminimp3.cmake", "minimp3", "MINIMP3")
        self.add_find_package_case("Findtheora.cmake", "theora", "THEORA")

        try:
            tools.rename("FindPhysFS.cmake", "Findphysfs.cmake")
        except:
            pass
        tools.replace_in_file("Findphysfs.cmake", "PhysFS", "physfs")
        self.add_find_package_case("Findphysfs.cmake", "physfs", "PHYSFS")

    def source(self):
        self.run("git clone https://github.com/liballeg/allegro5.git --depth=1 --single-branch --branch=5.2.7 source_subfolder")
        #tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)
        self._patch_sources()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["SHARED"] = False
        self._cmake.definitions["WANT_STATIC_RUNTIME"] = "MT" in msvc_runtime_flag(self) if self._is_msvc else False
        self._cmake.definitions["CMAKE_BUILD_TYPE"] = self.settings.build_type
        self._cmake.definitions["PREFER_STATIC_DEPS"] = True
        self._cmake.definitions["WANT_DOCS"] = False
        self._cmake.definitions["WANT_DOCS_HTML"] = False
        self._cmake.definitions["WANT_EXAMPLES"] = False
        self._cmake.definitions["WANT_FONT"] = True
        self._cmake.definitions["WANT_MONOLITH"] = True
        self._cmake.definitions["WANT_TESTS"] = False
        self._cmake.definitions["WANT_DEMO"] = False
        self._cmake.definitions["WANT_RELEASE_LOGGING"] = False
        self._cmake.definitions["WANT_VORBIS"] = True
        self._cmake.definitions["WANT_MP3"] = True
        self._cmake.definitions["WANT_OGG_VIDEO"] = True

        self._cmake.definitions["FREETYPE_ZLIB"] = self.options["freetype"].with_zlib
        self._cmake.definitions["FREETYPE_BZIP2"] = self.options["freetype"].with_bzip2
        self._cmake.definitions["FREETYPE_PNG"] = self.options["freetype"].with_png
        self._cmake.definitions["FREETYPE_HARFBUZZ"] = False
            
        self._cmake.definitions["CMAKE_CXX_FLAGS"] = "/wd4267 /wd4018 /Zc:externConstexpr" if self._is_msvc else "-Wno-unused-variable -w"
        
        self._cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["allegro_monolith-debug-static" if self.settings.build_type == "Debug" else "allegro_monolith-static"]
        self.cpp_info.defines = ["ALLEGRO_STATICLINK"]

        if self.settings.os == "Windows":
            self.cpp_info.system_libs = [ "opengl32", "shlwapi" ]
