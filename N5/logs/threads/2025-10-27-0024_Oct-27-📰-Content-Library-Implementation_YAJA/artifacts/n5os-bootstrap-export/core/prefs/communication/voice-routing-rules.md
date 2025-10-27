# Voice Routing Rules

**Version:** 1.0  
**Last Updated:** 2025-10-17

---

## Routing Logic

- **Social Media Voice** file (`social-media-voice.md`) is applied when the output:
  - Is a LinkedIn post, Twitter thread, newsletter, external blog, or publicly facing marketing content.

- **Core Voice** file (`voice.md` and related communication prefs) is applied when the output:
  - Is a professional email, one-to-one communication, formal document, internal memos, or other private/professional contexts.

## Fail-safes

- If the context is ambiguous, prompt for clarification before output generation.
- Log and alert if voice context conflicts occur to prevent style bleed.

## Versioning & References

- Both voice profiles are versioned independently but reference each other for shared foundational principles.
- Clear documentation indicates purpose and context for each voice.

---

## Future Considerations

- Potential hybrid voice for newsletters/blogs with nuanced context detection.
- Expansion to additional voice profiles for other channels as needed.