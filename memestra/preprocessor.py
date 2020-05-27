from nbconvert.preprocessors import Preprocessor
from memestra import nbmemestra
from traitlets import Tuple


class MemestraDeprecationChecker(Preprocessor):
    """A memestra-based preprocessor that checks code for places where deprecated functions are called"""

    decorator = Tuple(help="path to import the deprecation decorator, e.g. ('module', 'attribute')").tag(config=True)

    def preprocess(self, nb, resources):
        self.log.info("Using decorator '%s.%s' to check deprecated functions", self.decorator[0], self.decorator[1])
        deprecations = {}
        for d in nbmemestra.nbmemestra(nb, self.decorator):
            i = int(d[1].split('[', 1)[1].split(']')[0])
            deprecation = deprecations.get(i, [])
            deprecation.append(d)
            deprecations[i] = deprecation
        i = 0
        for cell in nb.cells:
            if cell['cell_type'] == 'code':
                if i in deprecations:
                    for d in deprecations[i]:
                        line = d[2]
                        col = d[3]
                        outputs = cell.get('outputs', [])
                        message = 'On line {}:\n'.format(line)
                        message += cell['source'].split('\n')[line - 1] + '\n'
                        message += ' ' * col + '^\n'
                        message += 'Warning: call to deprecated function {}'.format(d[0])
                        outputs.append({'output_type': 'stream', 'name': 'stderr', 'text': message})
                        cell['outputs'] = outputs
                i += 1
        return nb, resources
