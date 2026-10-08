# Migración 18.0 -> 19.0
# En 18 las restricciones únicas se definían con _sql_constraints con las claves
# 'name' y 'code' (nombres SQL l10n_ve_responsibility_type_name/_code). En 19 se
# definen con models.Constraint como _name_uniq/_code_uniq, por lo que el ORM
# crearía restricciones nuevas y dejaría las viejas duplicadas.
import logging

_logger = logging.getLogger(__name__)

OLD_CONSTRAINTS = (
    'l10n_ve_responsibility_type_name',
    'l10n_ve_responsibility_type_code',
)


def migrate(cr, version):
    if not version:
        return
    for name in OLD_CONSTRAINTS:
        cr.execute(
            "ALTER TABLE l10n_ve_responsibility_type DROP CONSTRAINT IF EXISTS %s" % name
        )
    cr.execute(
        "DELETE FROM ir_model_constraint WHERE name IN %s AND type = 'u'",
        (OLD_CONSTRAINTS,),
    )
    _logger.info("l10n_ve_base: eliminadas restricciones SQL de 18 %s", OLD_CONSTRAINTS)
