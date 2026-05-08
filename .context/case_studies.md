
### CS-024: QNAP RAID File Corruption (Event ID 51)
**Problem**: Plex server reporting file corruption for media stored on a QNAP TR-002 RAID 1 enclosure.
**Diagnosis**: chkdsk confirmed NTFS was 100% healthy. System Event Logs showed repeated Event ID 51 (paging operation error). QNAP External RAID Manager showed physical disks as Good.
**Solution**: Hardware failure isolated strictly to the USB bridge. Swapping the stock USB-C cable for a USB-A-to-C cable bypassed the faulty port/cable and dropped errors to zero.
**Key Insight**: Corruption during stream with a healthy filesystem is almost always a micro-disconnect at the hardware layer.

### CS-025: The Inflammatory Triad (Pelvic Cysts vs Autoimmune)
**Problem**: Patient with `TNF-Alpha A/G` variant experienced a massive inflammatory spike (CRP 9, Platelets 509, Ferritin 205) mimicking systemic autoimmune disease.
**Diagnosis**: Full systemic autoimmune panels (ANA, RF, Calprotectin, Coeliac) were negative. The triad of acute-phase reactants (CRP/Platelets/Ferritin) was traced to localized tissue damage from suspected pelvic functional cysts/endometriomas.
**Solution**: Pure NAC and high-dose Omega-3s bottlenecked the systemic cascade. Broad-spectrum CBD targeted as a pharmacological inhibitor for localized TNF-Alpha pain.
**Key Insight**: A localized cyst rupture in a patient with a `TNF-Alpha` variant can mimic a massive systemic autoimmune flare-up.
