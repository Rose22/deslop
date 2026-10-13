# DeSlop
*because why would you let an AI remove slop from your code when the AI is the one that caused the slop in the first place?*

A little tool i vibecoded (how ironic, right?) that lets me go through massive codebases that have marker comments like "AI GENERATED CODE", and then manually edit each occurence of it

It lets me review and edit ai generated code very fast, making sure it's up to my standards of quality, free of bugs, free of weird ai workarounds, spaghetti, and so on

To use this, instruct your ai to add a marker to each bit of code it adds, in this format:
```
# -- AI GENERATED CODE (model name) :: current_date
```

You can optionally add `harness:whatever` to mark what harness was used

If you want to review AI code but leave it as-is, you can use `status:reviewed` in the marker. Then it'll still clearly be marked as AI generated code, which i think is important, but be skipped by deslop. I personally believe that as soon as you make enough edits to AI generated code, it's become your code, and so you can remove the marker, since it's no longer just AI generated. This is the approach I use in my harness OpenLumara.