# Lingua course audio

This folder is ready for optional, properly licensed course recordings. No third-party copyrighted recordings are bundled.

## Folder structure

```text
audio/
├── manifest.json
├── sw/
├── fr/
├── es/
├── de/
├── it/
└── en/
```

You can add other language folders too: `lg`, `ach`, `luo`, `rw`, `pt`, `ar`, `hi`, `zh`, `ja`, `ko`.

## Mapping a recording

A course phrase is identified by `language-level-unit-phrase`, using zero-based unit and phrase numbers. For example, the first phrase in the first A1 unit of Kiswahili is `sw-A1-0-0`.

Put the recording at `audio/sw/A1-0-0.mp3`, then add this mapping to `audio/manifest.json`:

```json
{
  "version": 1,
  "languages": {
    "sw": {
      "sw-A1-0-0": "/audio/sw/A1-0-0.mp3"
    }
  }
}
```

Playback order is: licensed Lingua course recording → selected/detected browser voice → browser speech-engine fallback.

The Settings page shows how many recordings are mapped for each language.

Only add recordings you created yourself or have permission/licensing to use.
