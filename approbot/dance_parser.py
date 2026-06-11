def parse(path: str) -> dict:
    """Parse un fichier .dance.

    Retourne :
        {
            'moves':   [{'direction': str, 'count': int}, ...],
            'actions': {code_couleur: {'arms': [tokens], 'expression': token}, ...}
        }

    Format attendu :
        SEQ 1          ← ignoré
        1U             ← 1 pas direction U (U/B/L/R)
        2B
        ACT            ← séparateur
        N ARU ALB XNG  ← couleur puis tokens bras/expression
        B XSD
    """
    moves = []
    actions = {}
    in_actions = False

    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.upper().startswith('SEQ'):
                continue
            if line.upper() == 'ACT':
                in_actions = True
                continue

            if in_actions:
                parts = line.split()
                if len(parts) < 2:
                    continue
                color = parts[0].upper()
                tokens = parts[1:]
                arms = [t for t in tokens if t.startswith('A')]
                expressions = [t for t in tokens if t.startswith('X')]
                actions[color] = {
                    'arms': arms,
                    'expression': expressions[0] if expressions else 'XNT'
                }
            else:
                if len(line) < 2:
                    continue
                try:
                    count = int(line[:-1])
                    direction = line[-1].upper()
                    if direction in ('U', 'B', 'L', 'R'):
                        moves.append({'direction': direction, 'count': count})
                except ValueError:
                    pass

    return {'moves': moves, 'actions': actions}


def resume(dance: dict) -> str:
    """Retourne une description lisible d'une danse parsée."""
    noms_dir = {'U': 'avant', 'B': 'arrière', 'L': 'gauche', 'R': 'droite'}
    lignes = [f"Mouvements ({len(dance['moves'])}) :"]
    for i, m in enumerate(dance['moves'], 1):
        lignes.append(f"  {i}. {m['count']}x {noms_dir.get(m['direction'], m['direction'])}")

    if dance['actions']:
        lignes.append(f"Actions ({len(dance['actions'])}) :")
        for couleur, act in dance['actions'].items():
            bras = '+'.join(act['arms']) if act['arms'] else 'aucun'
            lignes.append(f"  {couleur} → bras: {bras}  expression: {act['expression']}")

    return '\n'.join(lignes)
