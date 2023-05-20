with open("style.css", "r") as f:
    code = f.read()

css = """
<style>
{code}
</style>
""".format(
    code=code
)
