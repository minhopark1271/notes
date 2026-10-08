# mesh-ops -- DashOpti mesh operator component (Jacobian check).
#
# This file is hand-maintained. The vcpkg.json next to it is NOT: scripts/update_version.py
# regenerates it from the source repository's manifest (regen_manifest), so change dependencies
# or features in DashOpti_MeshOps, not here.
#
# NOTE: keep this file ASCII. registry.py::PortInfo.from_files reads portfile.cmake with the
# platform default encoding (cp1252 on the CI runner) while to_files writes UTF-8, so non-ASCII
# bytes here crash render_readme.py. See the follow-up that adds encoding="utf-8" to the reads.
#
# ---------------------------------------------------------------------------
# If a feature is reintroduced
# ---------------------------------------------------------------------------
# MKL is unconditional: the source dropped the DASH_MO_WITH_MKL option and the no-mkl presets,
# so there is no option to forward. If it becomes selectable again, forward it with
# vcpkg_check_features() -- declaring a feature without passing it through makes configure fail
# for consumers who turn it off.
#
# default-features are `test` and `vcpkg-vtk`.
#   - test: pulls gtest, but the source gates tests on BUILD_TESTING / VCPKG_MANIFEST_FEATURES
#     and both are empty in a port build, so no test is built. gtest is installed and unused.
#     Removing it requires dropping the default in the source manifest.
#   - vcpkg-vtk: on by default, so vtk comes along. Do not build this port with
#     default-features disabled -- vtk would go missing.

# Pinned commit: "handle generator Options as the creation record, unique_ptr factories and
# {options, pose} persistence" (#14), 2026-10-04. Source version 0.5.0 -- no API or ABI
# guarantee from the 0.4.0 that was pinned before; consumers are locked with SameMinorVersion
# and must rebuild.
#
# The pinned REF is on dev, not main: DashOpti_MeshOps main trails dev, so the release line
# does not carry the development state. HEAD_REF main is left as written but does not describe
# this REF. See convention/repo-layout.md section 2.2.
#
# NOTE: keep comments out of the vcpkg_from_git block. registry.py matches
#   vcpkg_from_git\s*\(\s*[^)]*?REF\s+...
# so any closing paren between the call and REF -- including one inside a comment -- makes the
# match fail with "Missing REF".

vcpkg_from_git(
    OUT_SOURCE_PATH SOURCE_PATH
    URL https://github.com/NumeRealWorks/DashOpti_MeshOps.git
    REF 12796b8f236478a468d4e4ab3d31134eea33be0d
    HEAD_REF main
)

vcpkg_cmake_configure(
    SOURCE_PATH "${SOURCE_PATH}"
    OPTIONS
        # The external/ tree is not part of the port source; use the vcpkg vtk port.
        -DDASH_MO_VTK_EXTERNAL=OFF
)

vcpkg_cmake_install()

vcpkg_cmake_config_fixup()

# If the source's install(DIRECTORY include/ ...) also lands headers under debug/, vcpkg's
# post-build check rejects it ("Include files should not be duplicated into the /debug/include
# directory"). This is a no-op when the directory is absent. (config_fixup handles debug/share.)
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/include")

# No copyright file: the internal repository has no LICENSE, and the core-lib / reader-writer
# ports skip vcpkg_install_copyright for the same reason. Revisit if this ships publicly.
