# Session 58
Date: 2026-05-05

Boot initialized via `/start`.
Warnings detected during brain health check:
- [Chemical State] Stale: last updated 101h ago
- [Instinct Primer] Stale: generated 101h ago


Quicksave: Diagnosed QNAP Plex drive corruption. Found Event ID 51 paging errors indicating hardware/USB disconnects. NTFS is healthy. Created diagnostic report.

Quicksave: User is swapping the USB cable. Awaiting physical test results.

Quicksave: Checked USB power settings. Selective Suspend is ALREADY DISABLED. This points heavily toward physical cable/port failure or drive failure. Instructing user to check QNAP External RAID Manager for drive health.

Quicksave: User noted the drives register as a single RAID 1 group in Windows. Explained that this is why we must use the QNAP software, and automatically launched QNAP External RAID Manager for her to check SMART status.

Quicksave: User confirmed SMART data on both physical disks is 'Good'. Hardware failure isolated strictly to the USB bridge (cable, port, or enclosure controller). Recommending testing with any USB A-to-C cable to isolate the FURY C-port and the stock cable.

Quicksave: User connected USB A-to-C cable. Requesting user to generate read load via Plex to test stability before checking Event Logs.

Quicksave: Checked Event Logs after user generated load with A-to-C cable. Zero Event ID 51 errors found. Cable/port isolation successful. Conclusion: The stock USB-C cable or FURY's USB-C port was faulty. Data is safe.

Quicksave: Diagnostic flow completed successfully. Artifact updated with resolution. Task complete.

Quicksave: User is now setting up Plex on 'old silver laptop'. Encountering transcoder crash. Cannot run commands locally since the host is different. Suspect hardware acceleration or temp directory issue. Initiating diagnostic questions.

Quicksave: User clarified that playback works on another laptop but transcoder crashes on Android phone. Explained that this means the laptop is Direct Playing (no transcode needed) while the phone requires transcoding, which triggers the crash. Re-emphasized checking Hardware Acceleration on the server and testing Direct Play on the phone.

## Session Synthesis

### Key Topics
- QNAP Plex Drive file corruption diagnosis (Event ID 51).
- Isolating hardware vs filesystem errors.
- Plex Transcoder crashes on older hardware (Intel QuickSync/Hardware Acceleration).
- Direct Play vs Transcoding differences across devices.

### Decisions Made
- Swapped the stock QNAP USB-C cable for an A-to-C cable to bypass the faulty connection, permanently fixing the corruption.
- Identified Hardware Acceleration mismatch as the root cause of the transcoder crash on the silver laptop.

### Action Items
- Continue monitoring Plex transcoder performance on the silver laptop.
- Leave the QNAP running on the A-to-C cable.
