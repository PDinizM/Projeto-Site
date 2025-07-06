from typing import Any, Dict, Type

from sqlalchemy import inspect
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import DeclarativeMeta


def analisar_tabela(
    model_class: Type[DeclarativeMeta],
    engine: Engine,
    schema: str = "bethadba",
) -> Dict[str, Any]:
    inspector = inspect(engine)
    table_name: str = model_class.__tablename__

    # Obtém informações do banco de dados
    db_columns = inspector.get_columns(table_name, schema=schema)
    db_pk = inspector.get_pk_constraint(table_name, schema=schema)[
        "constrained_columns"
    ]
    db_fks = inspector.get_foreign_keys(table_name, schema=schema)  # Nova linha

    # Obtém informações do modelo
    model_columns = {column.key for column in model_class.__table__.columns}
    model_pk = [col.name for col in model_class.__table__.primary_key]

    # Processa as colunas
    defined_columns = []
    undefined_columns = []

    for col in db_columns:
        # Encontra FK correspondente (se existir)
        fk_info = next(
            (fk for fk in db_fks if col["name"] in fk["constrained_columns"]), None
        )

        column_info = {
            "name": col["name"],
            "type": str(col["type"]),
            "nullable": col["nullable"],
            "default": col["default"],
            "is_pk": col["name"] in db_pk,
            "is_fk": fk_info is not None,  # Nova informação
            "fk_reference": f"{fk_info['referred_schema']}.{fk_info['referred_table']}.{fk_info['referred_columns'][0]}"
            if fk_info
            else None,  # Nova informação
            "is_defined": col["name"].lower() in model_columns,
        }

        if column_info["is_defined"]:
            defined_columns.append(column_info)
        else:
            undefined_columns.append(column_info)

    return {
        "table_name": f"{schema}.{table_name}" if schema else table_name,
        "primary_keys": {"database": db_pk, "model": model_pk},
        "foreign_keys": db_fks,  # Nova informação
        "defined_columns": defined_columns,
        "undefined_columns": undefined_columns,
        "column_count": {
            "total": len(db_columns),
            "defined": len(defined_columns),
            "undefined": len(undefined_columns),
        },
    }


def imprimir_analise_tabela(resultado: Dict[str, Any]):
    """Imprime os resultados da análise de forma organizada."""
    print(f"\nAnálise da tabela: {resultado['table_name']}")
    print(f"\nPrimary Keys - Banco: {resultado['primary_keys']['database']}")

    # Nova seção para Foreign Keys
    if resultado["foreign_keys"]:
        print("\nForeign Keys encontradas no banco (agrupadas):")
        unique_fks = {}
        for fk in resultado["foreign_keys"]:
            key = (
                tuple(fk["constrained_columns"]),
                fk["referred_schema"],
                fk["referred_table"],
                tuple(fk["referred_columns"]),
            )
            unique_fks[key] = unique_fks.get(key, 0) + 1

        for (constrained, schema, table, referred), count in unique_fks.items():
            constraint_str = ", ".join(constrained)
            referred_str = ", ".join(referred)
            print(f"- {constraint_str} → {schema}.{table}({referred_str})")

    print("\nColunas NÃO DEFINIDAS no modelo:")
    for col in resultado["undefined_columns"]:
        pk = " (PK)" if col["is_pk"] else ""
        fk = f" (FK → {col['fk_reference']})" if col["is_fk"] else ""
        print(f"- {col['name'].lower()}: {col['type']}{pk}{fk}")

    print(
        f"\nResumo: {resultado['column_count']['defined']} definidas de {resultado['column_count']['total']} colunas"
    )
