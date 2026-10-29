<!-- DRAFT for edgi-govdata-archiving/ECHO_modules (no issue templates). Not posted; reviewed before posting. -->

**Title:** LICENSE is GPL-3.0, but the README says 3-Clause BSD and links to wayback's LICENSE

The repository states two different licences:

- **`LICENSE`** is the GNU GPL v3 (added in 741d2e3, 2021-06-10), and GitHub shows the repository as GPL-3.0.
- **The README's "License & Copyright" section** says: "This program is free software: you can redistribute it and/or modify it under the terms of the 3-Clause BSD License. See the `LICENSE <https://github.com/edgi-govdata-archiving/wayback/blob/master/LICENSE>` file for details." That link goes to the **wayback** repository's licence, so the paragraph looks copied from wayback's README.

The two licences ask very different things of anyone who builds on ECHO_modules or contributes to it: GPL-3.0's copyleft against BSD-3's permissive terms.

Which one is intended? I'm happy to open a PR that aligns the README or the `LICENSE` file, whichever you choose. I'd also like to contribute some analysis code here later, so I want to get the terms right first.

Drafted with an AI assistant (Claude); I read it before posting.
