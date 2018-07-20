# lute

Lute is a framework for writing NLU pipelines. The attempt is to provide an easy
way for writing composable modules that can be connected in arbitrary
_Make-like_ way to create complex NLU pipelines.

As of now the development focus is on creating a simple interface (similar to
keras) which lets us quickly prototype, test and deploy model improvements.

## Example

A model written in lute is a directed acyclic `graph` of `nodes`. A single
`node` is a logical unit like a preprocessor which takes output from its
predecessors and does something to it. The nodal computations are lazy and are
abstracted out in a `graph`. An example, with hypothetical nodes, follows:

```python
# Define an input placeholder (similar to tensorflow's)
text = Variable()
# Call other nodes to chain operations
normalized = Normalize("en")(text)
ngrams = Ngrams(n=2)(normalized)

# Lets do some rule based pattern searches
entities = EntitySearch(["date", "weather"])(normalized)
rule_intent = IntentPattern(["greet"])(entities, ngrams)

# A word vector based model in case the rules don't match
vector = SentVec("en")(normalized)
vector_intent = IntentVector("./model/path.hd5")(vector)

# Finally lets add a client specific node which might take care of deciding
# what to do when rules match and when to use input from the word vector
# model
result = ClientNode()([rule_intent, vector_intent])

# Put all together in a graph
# `text` is the input. For output we want the final `result` and also
# the parsed `entities`.
g = Graph(text, [result, entities])
g.run({ text: "Whats up people!" })

# This might return something like
["greet", []]
```
