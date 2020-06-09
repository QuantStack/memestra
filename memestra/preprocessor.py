import re
from nbconvert.preprocessors import Preprocessor
from memestra import nbmemestra
from traitlets import Tuple


class MemestraDeprecationChecker(Preprocessor):
    """A memestra-based preprocessor that checks code for places where deprecated functions are called"""

    decorator = Tuple(help="path to import the deprecation decorator, e.g. ('module', 'attribute')").tag(config=True)

    def preprocess(self, nb, resources):
        self.log.info("Using decorator '%s.%s' to check deprecated functions", self.decorator[0], self.decorator[1])
        deprecations = {}
        for d in nbmemestra.nbmemestra_from_nbnode(nb, self.decorator, ""):
            code_cell_i = int(re.search(r"\[(\d+)\]", d[1]).group(1))
            deprecation = deprecations.get(code_cell_i, [])
            deprecation.append(d)
            deprecations[code_cell_i] = deprecation
        # filter out non-code cell as it is done in nbmemestra
        code_cell_i = -1
        for cell in nb.cells:
            if cell['cell_type'] != 'code':
                continue
            code_cell_i += 1
            if code_cell_i not in deprecations:
                continue
            for d in deprecations[code_cell_i]:
                line, col = d[2:4]
                outputs = cell.get('outputs', [])
                message = ('On line {}:\n'
                           '{}\n'
                           '{}^\n'
                           'Warning: call to deprecated function {}'.format(
                               line,
                               cell['source'].split('\n')[line - 1],
                               ' ' * col,
                               d[0]
                          ))

                outputs.append({'output_type': 'stream', 'name': 'stderr', 'text': message})
                cell['outputs'] = outputs
        return nb, resources
