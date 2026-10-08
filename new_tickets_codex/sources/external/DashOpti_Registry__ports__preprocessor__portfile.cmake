# preprocessor -- DashOpti CAE result preprocessor (Abaqus ODB, Ansys Mechanical DPF, Ansys
# Motion DFR) behind one facade DLL; the tool plugins run in a separate worker process.
#
# This file is hand-maintained. The vcpkg.json next to it is NOT: scripts/update_version.py
# regenerates it from the source repository's manifest (regen_manifest), so change dependencies
# or features in DashOpti_Preprocessor, not here.
#
# NOTE: the first registration of a port skips that regeneration -- update_version.py treats a
# port absent at the merge base as authored-as-is. The manifest committed alongside this file
# was written to match DashOpti_Preprocessor/vcpkg.json by hand (host dependencies added, semver
# version replaced by version-date). Later PRs regenerate it normally.
#
# NOTE: keep this file ASCII (registry.py reads it with the platform default encoding) and keep
# comments out of the vcpkg_from_git block. registry.py matches
#   vcpkg_from_git\s*\(\s*[^)]*?REF\s+...
# so any closing paren between the call and REF -- including one inside a comment -- makes the
# match fail with "Missing REF".
#
# ---------------------------------------------------------------------------
# Build runner requirements (host SDKs, not vcpkg packages)
# ---------------------------------------------------------------------------
# The three tool plugins are configure options in the source (DASH_PR_WITH_ABAQUS,
# DASH_PR_WITH_ANSYS_MECHANICAL, DASH_PR_WITH_ANSYS_MOTION, all ON by default). They are passed
# explicitly below so the port never silently drops a plugin: when a host SDK is missing,
# configure fails with a FATAL_ERROR that names the missing path.
#
#   - Abaqus: headers + import libraries of each version in DASH_PR_ABAQUS_VERSIONS (source
#     default "2020" -- the runner has only the 2020 SDK; 2024 is opt-in until its snapshot is
#     on the runner). Nothing from Abaqus is linked statically or redistributed; the ODB runtime
#     comes from the consumer's Abaqus installation. Root: ABAQUS_BASE_DIR_2020
#     (default C:/SIMULIA/EstProducts/2020/ -- override with an OPTIONS entry if the runner
#     keeps its SDK snapshot elsewhere).
#   - Ansys Mechanical: nothing (the DPF client is vendored under source/AnsysMechanical/third_party).
#   - Ansys Motion: .NET Framework 4.8 SDK + targeting pack (the bridge is a /clr assembly).
#
# ---------------------------------------------------------------------------
# VTK
# ---------------------------------------------------------------------------
# The public API hands out vtkSmartPointer<vtkUnstructuredGrid>, so consumers must link the
# same VTK. vtk is a plain dependency of the source manifest (same feature string as mesh-ops so
# the binary cache is shared). There is no feature switch any more: the external/ pre-built axis
# and the vcpkg-vtk feature were removed upstream in 7e29fe4 (PR #4).
#
# The source manifest also pins opencascade 7.9.3#1 through `overrides` so that vtk[ioocct]
# resolves to the OCCT build already in the binary cache. vcpkg honours overrides only in a
# top-level manifest and regen_manifest strips them from this port, so every consumer must carry
# the same override itself -- DashOpti (meta) and DashOpti_GUI already do.
#
# ---------------------------------------------------------------------------
# bin/ is one bundle -- do not vcpkg_copy_tools
# ---------------------------------------------------------------------------
# The facade finds Preprocessor_Worker.exe only next to its own DLL (WorkerLocator), and the
# worker finds the plugin DLLs next to itself. Moving the exe to tools/ would make every
# SetPlugin fail with NotFound. VCPKG_POLICY_ALLOW_EXES_IN_BIN keeps the post-build check quiet.
# Consumers must redistribute bin/*.dll AND bin/*.exe (applocal copies only link dependencies).
# Since b1c0883 the package ships the rule for that: preprocessor-config.cmake includes
# dash-pr-copy-runtime.cmake, so a consumer calls dash_pr_copy_runtime(<target>) right after
# find_package(preprocessor CONFIG) and the worker exe plus plugin DLLs land next to its
# executable as a POST_BUILD step. share/preprocessor/usage says the same after install.
# See docs/consuming.md section 3 in the source repository.
#
# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
# The `test` feature is not a default feature, so the port build pulls no gtest and builds no
# test. Unit tests (label unit-test) and the integration / contract suites (label
# integration-test, which need Abaqus + test artifacts and, for Ansys Motion, user data) run in
# the meta repository's super build. This port is not yet in PORTS_WITH_INTEGRATION_TESTS
# (.github/workflows/pr-update-ports.yml); add it once the super build shows the labelled
# integration tests green on the runner.

# Pinned commit: "build(cmake): dash_pr_copy_runtime()" (PR #13), 2026-09-22 -- the package now
# installs the POST_BUILD rule that copies the runtime bundle next to the consumer executable
# (see the bin/ section above; DashOpti_GUI#518 is the failure it prevents). Two more commits
# ride along since the previous pin:
#   - 7e29fe4 (PR #4): the external VTK axis is gone -- option DASH_PR_VTK_EXTERNAL and feature
#     vcpkg-vtk no longer exist, vtk is a plain dependency, opencascade 7.9.3#1 override added
#     to the source manifest (see the VTK section above).
#   - 9042665 (PR #9): tools/gui-path-probe, a headless probe of the GUI call path. Top-level
#     builds only, not installed -- no effect on this port.
# dev (default) and main are fast-forwarded to the same commit, so HEAD_REF main is accurate.
#
# Previous pin aed93ab (2026-09-15, PR #2): WorkerTaskScope dangling context fix that hung the
# super build on the runner for 5 h 44 min (DashOpti#48).
# Before that 7f15a09 (2026-09-10): gtest discovery timeout raised to 120 s after the VTK 9.3
# compile fix (755897f).

vcpkg_from_git(
    OUT_SOURCE_PATH SOURCE_PATH
    URL https://github.com/NumeRealWorks/DashOpti_Preprocessor.git
    REF b1c08833754a29bc502945adc59c7f7990d128cb
    HEAD_REF main
)

vcpkg_cmake_configure(
    SOURCE_PATH "${SOURCE_PATH}"
    OPTIONS
        # Explicit so a missing host SDK is a configure failure, never a silently absent plugin.
        -DDASH_PR_WITH_ABAQUS=ON
        -DDASH_PR_WITH_ANSYS_MECHANICAL=ON
        -DDASH_PR_WITH_ANSYS_MOTION=ON
)

vcpkg_cmake_install()

vcpkg_cmake_config_fixup()

vcpkg_copy_pdbs()

# Preprocessor_Worker.exe must stay in bin/ next to the facade DLL (see above).
set(VCPKG_POLICY_ALLOW_EXES_IN_BIN enabled)

# If the source's install(DIRECTORY include/ ...) also lands headers under debug/, vcpkg's
# post-build check rejects it. This is a no-op when the directory is absent.
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/include")

# No copyright file: the internal repository has no LICENSE, and the sibling ports skip
# vcpkg_install_copyright for the same reason. Revisit if this ships publicly.
