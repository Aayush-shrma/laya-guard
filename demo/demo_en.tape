# Renders demo/demo_en.gif from the English mock demo (no model download).
# Run from repo root:  vhs demo/demo_en.tape
# NOTE: VHS Hide breaks Sleep capture, so the tape types visibly.
Output "demo/demo_en.gif"
Set Shell "bash"
Set FontSize 14
Set Width 1100
Set Height 800
Set Padding 20
Type "bash demo/demo_en.sh" Enter
Sleep 9s
