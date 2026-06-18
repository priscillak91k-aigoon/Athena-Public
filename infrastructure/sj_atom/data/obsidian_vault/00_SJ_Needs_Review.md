# SJ Companion Dashboard

## 🧠 Pending Profile Proposals
```dataview
LIST file.mtime
FROM "SJ_Core_Profile_proposals"
WHERE file.name != "SJ_Core_Profile_proposal_template"
```

## ⚠️ Quarantined Items
```dataview
LIST file.ctime
FROM "Quarantine"
```
