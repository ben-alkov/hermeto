# SPDX-License-Identifier: GPL-3.0-or-later
"""Data models for pip package manager artifacts and dependencies."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Union


@dataclass
class CommonArtifact:
    """Base class for representing a packaged Python artifact.
    
    This replaces the ad-hoc dict[str, Any] usage throughout the pip package manager
    with a structured, type-safe approach.
    """
    
    package: str
    """The package name."""
    
    path: Path
    """Path where the artifact is stored locally."""
    
    requirement_file: str
    """Path to the requirements file that specified this dependency."""
    
    missing_req_file_checksum: bool
    """Whether this artifact is missing checksums in the requirements file."""
    
    build_dependency: bool
    """Whether this is a build-time dependency (from requirements-build.txt)."""

    @property
    def kind(self) -> Literal["pypi", "url", "vcs"]:
        """Return the type of artifact for backward compatibility."""
        if isinstance(self, PyPIArtifact):
            return "pypi"
        elif isinstance(self, URLArtifact):
            return "url"
        elif isinstance(self, VCSArtifact):
            return "vcs"
        else:
            raise ValueError(f"Unknown artifact type: {type(self)}")


@dataclass
class PyPIArtifact(CommonArtifact):
    """Artifact downloaded from a Python Package Index (e.g., PyPI)."""
    
    index_url: str
    """URL of the package index."""
    
    package_type: Literal["sdist", "wheel"]
    """Type of Python package distribution."""
    
    version: str
    """Version string of the package."""


@dataclass
class VCSArtifact(CommonArtifact):
    """Artifact downloaded from a version control system (e.g., git)."""
    
    url: str
    """The VCS URL."""
    
    host: str
    """The VCS host (e.g., github.com)."""
    
    namespace: str
    """The namespace/organization (e.g., 'containerbuildsystem')."""
    
    repo: str
    """The repository name."""
    
    ref: str
    """The git reference (commit hash, branch, tag)."""

    @property
    def version(self) -> str:
        """Return version string for VCS artifacts."""
        return f"git+{self.url}@{self.ref}"


@dataclass
class URLArtifact(CommonArtifact):
    """Artifact downloaded from a direct URL."""
    
    original_url: str
    """The original URL specified in requirements."""
    
    url_with_hash: str
    """The URL with hash fragment added if needed."""

    @property
    def version(self) -> str:
        """Return version string for URL artifacts."""
        return self.url_with_hash


# Type alias for any artifact download
ArtifactDownload = Union[PyPIArtifact, VCSArtifact, URLArtifact]