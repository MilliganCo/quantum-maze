# Quantum Maze

> Public source preview: see [PUBLICATION.md](PUBLICATION.md) for actual checks, known failures and runtime limits.

## Описание

Экспериментальная игра-лабиринт на `pygame`, где генерация структуры уровня завязана на квантовую случайность через `Qiskit`. Проект сочетает процедурный лабиринт, ASCII-визуализацию и идею использования локального квантового симулятора как источника вариативности.

## Что внутри

- генерация лабиринта с помощью квантовых выборок;
- локальный запуск через `qasm_simulator`;
- графическое окно на `pygame`;
- игровая логика перемещения по процедурному уровню.

## Стек

- Python
- pygame
- qiskit
- qiskit-aer

## Запуск

```bash
pip install pygame qiskit qiskit-aer qiskit-ibm-runtime
python go.py
```

## Статус

WIP. Это исследовательский прототип на стыке генеративного геймдева и квантовых экспериментов.


## Public source status — 2026-10-29

See [PUBLICATION.md](PUBLICATION.md) for the current verification scope, prototype limitations and runtime boundaries. Earlier audit checklists describe historical work.
