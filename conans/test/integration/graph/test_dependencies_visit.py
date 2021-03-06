import textwrap

from conans.test.assets.genconanfile import GenConanfile
from conans.test.utils.tools import TestClient


def test_dependencies_visit():
    client = TestClient()
    client.save({"conanfile.py": GenConanfile()})
    client.run("create . openssl/0.1@")
    client.run("create . openssl/0.2@")
    client.save({"conanfile.py": GenConanfile().with_requires("openssl/0.2")})
    client.run("create . cmake/0.1@")
    conanfile = textwrap.dedent("""
        from conans import ConanFile
        class Pkg(ConanFile):
            requires = "openssl/0.1"
            build_requires = "cmake/0.1"

            def generate(self):
                dep = self.dependencies["openssl"]
                self.output.info("DefRef: {}!!!".format(repr(dep.ref)))
                self.output.info("DefPRef: {}!!!".format(repr(dep.pref)))
                dep = self.dependencies.build["openssl"]
                self.output.info("DefRefBuild: {}!!!".format(repr(dep.ref)))
                self.output.info("DefPRefBuild: {}!!!".format(repr(dep.pref)))
                for r, d in self.dependencies.build.items():
                    self.output.info("DIRECTBUILD {}: {}".format(r.direct, d))
        """)
    client.save({"conanfile.py": conanfile})
    client.run("install . -s:b os=Windows")  # Use 2 contexts
    assert "DefRef: openssl/0.1#f3367e0e7d170aa12abccb175fee5f97!!!" in client.out
    assert "DefPRef: openssl/0.1#f3367e0e7d170aa12abccb175fee5f97:"\
           "5ab84d6acfe1f23c4fae0ab88f26e3a396351ac9#"\
           "83c38d3b4e5f1b8450434436eec31b00!!!" in client.out

    assert "DefRefBuild: openssl/0.2#f3367e0e7d170aa12abccb175fee5f97!!!" in client.out
    assert "DefPRefBuild: openssl/0.2#f3367e0e7d170aa12abccb175fee5f97:" \
           "5ab84d6acfe1f23c4fae0ab88f26e3a396351ac9#" \
           "83c38d3b4e5f1b8450434436eec31b00!!!" in client.out

    assert "conanfile.py: DIRECTBUILD True: cmake/0.1" in client.out
    assert "conanfile.py: DIRECTBUILD False: openssl/0.2" in client.out
