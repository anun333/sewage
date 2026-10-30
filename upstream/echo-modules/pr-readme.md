<!-- Draft, not posted. A maintainer answered #140 on 2026-10-29 ("The actual license is GPL v3 ... Please feel free to update the readme!"). Opening it needs a fork, anun333/ECHO_modules, from main at fc2ddd9. No open PR touches README.md (checked 2026-10-30: #28, #32, #33). -->

**Title:** README: the licence is GPL v3 (closes #140)

**Body:**

As discussed in #140, the README's License section said 3-Clause BSD and linked to the wayback repository's LICENSE. This replaces that paragraph with the wording EDGI's other GPL-3.0 repositories use (web-monitoring-processing, web-monitoring-db, web-monitoring-ui), and links to this repository's own LICENSE. The link is absolute because PyPI shows this README too. The copyright line is unchanged.

Closes #140.

Drafted with an AI assistant (Claude); I read it before posting.

**Commit message:**

```
README: the licence is GPL v3, not 3-Clause BSD (#140)

The License section was copied from wayback's README and linked to its
LICENSE. Use the wording of EDGI's other GPL-3.0 repositories and link
to this repository's LICENSE.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

**The change** (README.md, the last paragraph):

```diff
--- a/README.md
+++ b/README.md
@@ -164,4 +164,8 @@
 --------------------------
 Copyright (C) 2019-2025 Environmental Data and Governance Initiative (EDGI)
 
-This program is free software: you can redistribute it and/or modify it under the terms of the 3-Clause BSD License. See the `LICENSE <https://github.com/edgi-govdata-archiving/wayback/blob/master/LICENSE>` file for details.
+This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 3.0.
+
+This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
+
+See the [`LICENSE`](https://github.com/edgi-govdata-archiving/ECHO_modules/blob/main/LICENSE) file for details.
```
