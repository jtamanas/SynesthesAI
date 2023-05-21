prompt = """Here's a synopsis of TOML Basic Elements:

* Comments in TOML begins with the (#) character.
* Comments must be separated from other tokens by whitespaces.
* Indentation of whitespace is used to denote structure.
* Tabs are not included as indentation for TOML files.
* List members are denoted by a leading hyphen (-).
* List members are enclosed in square brackets and separated by commas.
* Associative arrays are represented using colon ( : ) in the format of key value pair. They are enclosed in curly braces.
* Documents begin and end with 3 hyphens (---).
* Repeated nodes in each file are initially denoted by an ampersand (&) and by an asterisk (*) mark later.
* TOML always requires colons and commas used as list separators followed by space with scalar values.
* Nodes should be labelled with an exclamation mark (!) or double exclamation mark (!!), followed by string which can be expanded into an URI or URL.

The user will supply a TOML file that contains errors. Your job is to fix it using the principles above.
"""