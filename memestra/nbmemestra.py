from memestra import memestra
from io import StringIO
from collections import namedtuple
import nbformat


def nbmemestra_from_nbnode(nb, decorator, filepath):
    # Get code cells
    cells = nb.cells
    code_cells = [c for c in cells if c['cell_type'] == 'code']
    Cell = namedtuple('Cell', 'id begin end')
    # Aggregate code cells and generate cells list
    code_list = []
    cell_list = []
    current_line = 1
    for (num, c) in enumerate(code_cells):
        nb_lines = c['source'].count('\n') + 1
        code_list.append(c['source'])
        end_line = current_line + nb_lines
        cell_list.append(Cell(num, current_line, end_line))
        current_line = end_line
    code = '\n'.join(code_list)

    # Collect calls to deprecated functions
    deprecated_list = memestra(StringIO(code), decorator, filepath)

    # Map them to cells
    result = []
    for d in deprecated_list:
        cell = next(x for x in cell_list if x.begin <= d[2] and d[2] < x.end)
        result.append((d[0],
                       'Cell[' + str(cell.id) + ']', d[2] - cell.begin + 1,
                       d[3]))

    return result


def nbmemestra(nbfile, decorator, filepath):
    nb = nbformat.read(nbfile, 4)
    return nbmemestra_from_nbnode(nb, decorator, filepath)


def register(dispatcher):
    dispatcher['.ipynb'] = nbmemestra
