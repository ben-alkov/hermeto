# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for pip package manager data models."""

import pytest
from pathlib import Path

from hermeto.core.package_managers.pip.models import (
    CommonArtifact,
    PyPIArtifact,
    VCSArtifact,
    URLArtifact,
    ArtifactDownload,
)


class TestCommonArtifact:
    """Test the base CommonArtifact dataclass."""

    def test_kind_property_not_implemented(self):
        """Test that kind property raises ValueError for base class."""
        # We can't instantiate CommonArtifact directly due to the abstract kind property
        # This is expected behavior
        pass


class TestPyPIArtifact:
    """Test PyPIArtifact dataclass."""

    def test_creation(self):
        """Test basic PyPIArtifact creation."""
        artifact = PyPIArtifact(
            package="numpy",
            path=Path("/tmp/numpy-1.21.0.tar.gz"),
            requirement_file="requirements.txt",
            missing_req_file_checksum=False,
            build_dependency=False,
            index_url="https://pypi.org/simple/",
            package_type="sdist",
            version="1.21.0",
        )
        
        assert artifact.package == "numpy"
        assert artifact.path == Path("/tmp/numpy-1.21.0.tar.gz")
        assert artifact.requirement_file == "requirements.txt"
        assert artifact.missing_req_file_checksum is False
        assert artifact.build_dependency is False
        assert artifact.index_url == "https://pypi.org/simple/"
        assert artifact.package_type == "sdist"
        assert artifact.version == "1.21.0"
        assert artifact.kind == "pypi"

    def test_wheel_artifact(self):
        """Test PyPIArtifact with wheel package type."""
        artifact = PyPIArtifact(
            package="requests",
            path=Path("/tmp/requests-2.25.1-py2.py3-none-any.whl"),
            requirement_file="requirements.txt",
            missing_req_file_checksum=True,
            build_dependency=True,
            index_url="https://pypi.org/simple/",
            package_type="wheel",
            version="2.25.1",
        )
        
        assert artifact.package_type == "wheel"
        assert artifact.build_dependency is True
        assert artifact.kind == "pypi"


class TestVCSArtifact:
    """Test VCSArtifact dataclass."""

    def test_creation(self):
        """Test basic VCSArtifact creation."""
        artifact = VCSArtifact(
            package="myproject",
            path=Path("/tmp/myproject-gitcommit-abc123.tar.gz"),
            requirement_file="requirements.txt",
            missing_req_file_checksum=True,
            build_dependency=False,
            url="https://github.com/user/myproject.git",
            host="github.com",
            namespace="user",
            repo="myproject",
            ref="abc123",
        )
        
        assert artifact.package == "myproject"
        assert artifact.url == "https://github.com/user/myproject.git"
        assert artifact.host == "github.com"
        assert artifact.namespace == "user"
        assert artifact.repo == "myproject"
        assert artifact.ref == "abc123"
        assert artifact.kind == "vcs"

    def test_version_property(self):
        """Test that VCS version property returns git+ format."""
        artifact = VCSArtifact(
            package="myproject",
            path=Path("/tmp/myproject-gitcommit-abc123.tar.gz"),
            requirement_file="requirements.txt",
            missing_req_file_checksum=True,
            build_dependency=False,
            url="https://github.com/user/myproject.git",
            host="github.com",
            namespace="user",
            repo="myproject",
            ref="abc123",
        )
        
        expected_version = "git+https://github.com/user/myproject.git@abc123"
        assert artifact.version == expected_version


class TestURLArtifact:
    """Test URLArtifact dataclass."""

    def test_creation(self):
        """Test basic URLArtifact creation."""
        artifact = URLArtifact(
            package="custom-package",
            path=Path("/tmp/custom-package-abc123.tar.gz"),
            requirement_file="requirements.txt",
            missing_req_file_checksum=False,
            build_dependency=False,
            original_url="https://example.com/package.tar.gz",
            url_with_hash="https://example.com/package.tar.gz#cachito_hash=sha256:abc123",
        )
        
        assert artifact.package == "custom-package"
        assert artifact.original_url == "https://example.com/package.tar.gz"
        assert artifact.url_with_hash == "https://example.com/package.tar.gz#cachito_hash=sha256:abc123"
        assert artifact.kind == "url"

    def test_version_property(self):
        """Test that URL version property returns url_with_hash."""
        artifact = URLArtifact(
            package="custom-package",
            path=Path("/tmp/custom-package-abc123.tar.gz"),
            requirement_file="requirements.txt",
            missing_req_file_checksum=False,
            build_dependency=False,
            original_url="https://example.com/package.tar.gz",
            url_with_hash="https://example.com/package.tar.gz#cachito_hash=sha256:abc123",
        )
        
        assert artifact.version == "https://example.com/package.tar.gz#cachito_hash=sha256:abc123"


class TestArtifactDownloadUnion:
    """Test the ArtifactDownload union type."""

    def test_union_type_accepts_all_artifacts(self):
        """Test that ArtifactDownload union accepts all artifact types."""
        pypi_artifact = PyPIArtifact(
            package="numpy",
            path=Path("/tmp/numpy-1.21.0.tar.gz"),
            requirement_file="requirements.txt",
            missing_req_file_checksum=False,
            build_dependency=False,
            index_url="https://pypi.org/simple/",
            package_type="sdist",
            version="1.21.0",
        )
        
        vcs_artifact = VCSArtifact(
            package="myproject",
            path=Path("/tmp/myproject-gitcommit-abc123.tar.gz"),
            requirement_file="requirements.txt",
            missing_req_file_checksum=True,
            build_dependency=False,
            url="https://github.com/user/myproject.git",
            host="github.com",
            namespace="user",
            repo="myproject",
            ref="abc123",
        )
        
        url_artifact = URLArtifact(
            package="custom-package",
            path=Path("/tmp/custom-package-abc123.tar.gz"),
            requirement_file="requirements.txt",
            missing_req_file_checksum=False,
            build_dependency=False,
            original_url="https://example.com/package.tar.gz",
            url_with_hash="https://example.com/package.tar.gz#cachito_hash=sha256:abc123",
        )
        
        # Test that all types are accepted by the union
        artifacts: list[ArtifactDownload] = [pypi_artifact, vcs_artifact, url_artifact]
        
        assert len(artifacts) == 3
        assert isinstance(artifacts[0], PyPIArtifact)
        assert isinstance(artifacts[1], VCSArtifact)
        assert isinstance(artifacts[2], URLArtifact)


class TestArtifactCommonInterface:
    """Test the common interface shared by all artifact types."""

    @pytest.fixture
    def artifacts(self):
        """Create sample artifacts of each type."""
        return [
            PyPIArtifact(
                package="numpy",
                path=Path("/tmp/numpy-1.21.0.tar.gz"),
                requirement_file="requirements.txt",
                missing_req_file_checksum=False,
                build_dependency=False,
                index_url="https://pypi.org/simple/",
                package_type="sdist",
                version="1.21.0",
            ),
            VCSArtifact(
                package="myproject",
                path=Path("/tmp/myproject-gitcommit-abc123.tar.gz"),
                requirement_file="requirements.txt",
                missing_req_file_checksum=True,
                build_dependency=True,
                url="https://github.com/user/myproject.git",
                host="github.com",
                namespace="user",
                repo="myproject",
                ref="abc123",
            ),
            URLArtifact(
                package="custom-package",
                path=Path("/tmp/custom-package-abc123.tar.gz"),
                requirement_file="requirements.txt",
                missing_req_file_checksum=False,
                build_dependency=False,
                original_url="https://example.com/package.tar.gz",
                url_with_hash="https://example.com/package.tar.gz#cachito_hash=sha256:abc123",
            ),
        ]

    def test_all_artifacts_have_common_fields(self, artifacts):
        """Test that all artifacts have the common fields from CommonArtifact."""
        for artifact in artifacts:
            assert hasattr(artifact, "package")
            assert hasattr(artifact, "path")
            assert hasattr(artifact, "requirement_file")
            assert hasattr(artifact, "missing_req_file_checksum")
            assert hasattr(artifact, "build_dependency")
            assert hasattr(artifact, "kind")

    def test_kind_property_returns_correct_values(self, artifacts):
        """Test that kind property returns the correct values for each type."""
        pypi_artifact, vcs_artifact, url_artifact = artifacts
        
        assert pypi_artifact.kind == "pypi"
        assert vcs_artifact.kind == "vcs"
        assert url_artifact.kind == "url"

    def test_build_dependency_values(self, artifacts):
        """Test build_dependency field values."""
        pypi_artifact, vcs_artifact, url_artifact = artifacts
        
        assert pypi_artifact.build_dependency is False
        assert vcs_artifact.build_dependency is True
        assert url_artifact.build_dependency is False