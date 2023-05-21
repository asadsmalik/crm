from typing import List

from django.db import models, transaction


def save_models_in_transaction(model_list: List[models.Model]):
    with transaction.atomic():
        [model.save() for model in model_list]
