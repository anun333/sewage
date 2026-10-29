<!-- Posted 2026-10-29 as https://github.com/PHES-ODM/PHES-ODM/issues/296 after the maintainer read and approved this text. -->

**Title:** LICENSE says `cc-by-4.0` but holds CC BY-SA 4.0's legal text, while the README says CC BY 4.0

The repository states two different licences:

- **README.** The badge and the License section say CC BY 4.0: "Website content is published under a Creative Commons CC BY 4.0 license".
- **`LICENSE`.** The first line is `cc-by-4.0`, but the text below it is the legal code of **Attribution-ShareAlike** 4.0 International. GitHub's licence detection reads the file as CC-BY-SA-4.0, and the repository page shows that.

**The ShareAlike text looks accidental.** Commit 0e5a866 (2020-10-09), titled "update license to cc-by-4.0", replaced the MIT licence with that header and the BY-SA legal code. The intent in its title and in the README is CC BY 4.0.

**It matters to anyone adapting the dictionary.** Under BY-SA, adaptations have to be released under BY-SA as well; under BY, attribution is enough. Someone mapping the ODM into another schema, or building a derived standard, can't tell today which applies.

**A suggestion.**
- If CC BY 4.0 is intended, replace the text in `LICENSE` with CC BY 4.0's legal code (https://creativecommons.org/licenses/by/4.0/legalcode.txt).
- If ShareAlike is intended, update the README's badge and License section instead.

I'm happy to open a PR for either.

Drafted with an AI assistant (Claude); I read it before posting.
