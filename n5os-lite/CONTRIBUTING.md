# Contributing to N5OS Lite

Thank you for your interest in contributing! N5OS Lite is a community-driven project for enhancing AI-assisted work.

## How to Contribute

### 1. Share Your Workflows

**Contribute prompts:**
- Create reusable workflows you've found valuable
- Use proper YAML frontmatter (see `prompts/create-prompt.md`)
- Include clear examples and quality checks
- Test in fresh thread (P12) before submitting

**Submit via:**
- Pull Request to `prompts/` directory
- Discussion post with your workflow
- Issue with "workflow-idea" label

### 2. Extend Principles

**Contribute principles:**
- Document patterns you've discovered
- Use YAML format (see existing principles)
- Include when_to_apply, examples, anti_patterns
- Reference related principles

**Good candidates:**
- Recurring problems you've solved
- Lessons from production usage
- Patterns that save time/prevent errors

### 3. Improve Documentation

**Help others learn:**
- Clarify confusing sections
- Add more examples
- Create tutorials or guides
- Translate to other languages

### 4. Build Integrations

**Extend N5OS Lite:**
- Scripts for common tasks
- Integrations with tools/services
- Example projects using N5OS
- Templates for specific domains

## Contribution Guidelines

### Quality Standards

**For Prompts:**
- Clear, specific instructions
- Concrete examples (not generic)
- Quality checks included
- Tested and validated
- Follows P1 (Human-Readable First)

**For Principles:**
- Addresses specific, recurring problem
- Includes real examples
- Not too abstract or generic
- Has actionable anti-patterns
- Complements existing principles

**For Documentation:**
- Clear and concise
- Assumes beginner-friendly
- Includes examples
- No jargon without explanation

### Process

1. **Fork the repository**
2. **Create a branch** (`git checkout -b feature/your-contribution`)
3. **Make your changes** (follow existing patterns)
4. **Test thoroughly** (especially prompts - use P12)
5. **Commit with clear message** (what and why)
6. **Submit Pull Request** with description

### PR Template

```markdown
## What

{Brief description of contribution}

## Why

{Problem it solves or value it adds}

## Testing

{How you validated it works}

## Related

{Issues, discussions, or principles it relates to}
```

## What We're Looking For

### High Priority

- **Domain-specific prompts** (software dev, content creation, data analysis)
- **Real-world examples** showing N5OS in action
- **Integration guides** for popular tools
- **Improved onboarding** making it easier for newcomers

### Medium Priority

- **Additional personas** for specialized domains
- **Extended principles** from production lessons
- **Better tooling** (scripts, automation)
- **Video tutorials** or screencasts

### Not Accepting

- **Breaking changes** to core system (discuss first)
- **Overly complex** additions (keep it simple)
- **Proprietary integrations** requiring paid services
- **Duplicate functionality** (improve existing instead)

## Code of Conduct

### Be Respectful

- Assume good intent
- Provide constructive feedback
- Welcome newcomers
- Keep discussions professional

### Be Collaborative

- Build on others' work
- Give credit generously
- Help review PRs
- Share knowledge freely

### Be Principled

- Follow N5OS principles in contributions
- Prioritize accuracy over sophistication (P16)
- Document assumptions (P21)
- Complete work before claiming done (P15)

## Recognition

Contributors are recognized in:
- README contributors section
- Release notes for significant contributions
- Discussion shout-outs
- Commit history (permanent record)

## Questions?

- **Discussions:** Ask in GitHub Discussions
- **Issues:** Open issue with "question" label
- **Discord:** Join community (link in README)

## Getting Help

**Stuck on contribution?**
1. Check existing examples
2. Ask in Discussions
3. Reference principles for guidance
4. Start small and iterate

**Not sure if idea is good?**
1. Open Discussion post
2. Get feedback from community
3. Prototype and share
4. Iterate based on feedback

---

**We appreciate your contributions!**

Every improvement, no matter how small, makes N5OS Lite better for everyone.

---

*Last Updated: 2025-11-03*
