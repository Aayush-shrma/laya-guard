# Renders demo/demo.gif from the mock demo (no model download).
# Run from repo root:  vhs demo/demo.tape
Output "demo/demo.gif"
Set Shell "bash"
Set FontSize 14
Set Width 1100
Set Height 800
Set Padding 20
Type "bash demo/demo.sh" Enter
Sleep 9s
