"""Este script calcula uma pena com base nos critérios da lei.

:author: Paulo Santos (pauloxrms@gmail.com)
:copyright: Copyright (c) 2024, Paulo R.
"""

WEIGHT_FIRST_STEP = 1 / 8  # Fração de cada critério da primeira fase.

WEIGHT_SECOND_STEP = 1 / 6  # Fração de cada critério da segunda fase.

DAYS_IN_MONTH = 30  # Dias em um mês.

MONTHS_IN_YEAR = 12  # Meses em um ano.

DAYS_IN_YEAR = DAYS_IN_MONTH * MONTHS_IN_YEAR  # Dias em um ano.


class Sentence:
    """
    Classe de armazenamento e manipulação de sentenças.
    """

    def __init__(self):
        self.raw_days: int = 0
        self.years: int = 0
        self.months: int = 0
        self.raw_months: int = 0
        self.days: int = 0

    def __update(self):
        """
        Atualiza a sentença com base nos dias absolutos.
        """

        self.days = self.raw_days % DAYS_IN_MONTH
        self.raw_months = self.raw_days // DAYS_IN_MONTH
        self.months = self.raw_months % MONTHS_IN_YEAR
        self.years = self.raw_months // MONTHS_IN_YEAR

    def adjust(self, days: int):
        """
        Ajusta a sentença conforme a quantidade dada de dias.

        :param days: Dias para ajustar a sentença.
        :return: Sentença atualizada.
        """

        self.raw_days += days
        self.__update()
        return self

    def to_str(self, *, raw_days: bool = False, start: bool = True, end: bool = True):
        """
        Converte uma sentença para uma string formatada.

        :param raw_days: Mostrar apenas os dias absolutos.
        :param start: Formatar como início de frase.
        :param end: Formatar como fim de frase.
        :return: String formatada.
        """

        ret_str = ""

        if start:
            ret_str += "A pena é de "

        if raw_days or self.raw_days == 0:
            ret_str += f"{self.raw_days} dias"
        else:
            if self.years:
                ret_str += f"{self.years} anos"
            if self.months and self.days:
                ret_str += (", " if self.years else "") + f"{self.months} meses"
            elif self.months:
                ret_str += (" e " if self.years else "") + f"{self.months} meses"
            if self.days:
                ret_str += (" e " if (self.years or self.months) else "") + f"{self.days} dias"

        return ret_str + ("." if end else "")


class Crime:
    """
    Classe para armazenar e manipular um crime com base em sua dosimetria.
    """

    def __init__(self, *, name: str = None, min_sentence: str, max_sentence: str):
        """
        Cria um crime para dosimetria.

        :param name: Nome do crime, opcional.
        :param min_sentence: Pena mínima.
        :param max_sentence: Pena máxima.
        """

        min_amount = int(min_sentence[:-1])
        max_amount = int(max_sentence[:-1])

        self.name = name.strip().lower() if name is not None else None
        self.__evaluated_steps_mask: int = 0
        self.min_sentence_days = (
                min_amount * DAYS_IN_MONTH) if min_sentence[-1] == "m" else min_amount * DAYS_IN_YEAR
        self.max_sentence_days = (
                max_amount * DAYS_IN_MONTH) if max_sentence[-1] == "m" else max_amount * DAYS_IN_YEAR
        self.sentence = Sentence()
        self.sentence.adjust(self.min_sentence_days)
        print(f"Para o crime {f'de {self.name}' if self.name else 'avaliado'}, pena mínima é de "
              f"{self.sentence.to_str(start=False)}")

    def evaluate_first_step(self, first_step_valid_criteria: int):
        """
        Realiza a dosimetria da primeira fase.

        :param first_step_valid_criteria: Quantidade de critérios avaliados negativamente na primeira fase.
        """

        if self.__evaluated_steps_mask & 1:
            print(f"{'Crime' if self.name is None else self.name.capitalize()} já avaliado na primeira fase.")
            return

        self.__evaluated_steps_mask |= 1 << 0

        sentence_range_days = self.max_sentence_days - self.min_sentence_days
        criteria_weight_days = sentence_range_days * WEIGHT_FIRST_STEP
        first_step_delta_days = int(criteria_weight_days * max(min(8, first_step_valid_criteria), 0))

        self.sentence.adjust(first_step_delta_days)
        print(f"A pena após valoração da 1ª fase é de {self.sentence.to_str(start=False, end=False)} "
              f"(+{first_step_delta_days / DAYS_IN_MONTH:.1f} meses).")

    def evaluate_second_step(self, *, aggravating_count: int, mitigating_count: int):
        """
        Realiza a dosimetria da segunda fase.

        :param aggravating_count: Quantidade de agravantes.
        :param mitigating_count: Quantidade de atenuantes.
        """

        if not self.__evaluated_steps_mask & 1:
            print(f"O {self.name if self.name else 'crime'} ainda não foi avaliado na primeira fase.")
            return

        if self.__evaluated_steps_mask & 1 << 1:
            print(f"{self.name.capitalize() if self.name else 'Crime'} já avaliado na segunda fase.")
            return

        self.__evaluated_steps_mask |= 1 << 1

        criteria_weight_days = self.sentence.raw_days * WEIGHT_SECOND_STEP
        second_step_delta_days = int(criteria_weight_days * (aggravating_count - mitigating_count))

        self.sentence.adjust(second_step_delta_days)
        print(f"A pena após valoração da 2ª fase é de {self.sentence.to_str(start=False, end=False)} "
              f"({'+' if second_step_delta_days >= 0 else ''}{second_step_delta_days / DAYS_IN_MONTH:.1f} meses).")


if __name__ == "__main__":
    test_crime = Crime(min_sentence="6a", max_sentence="20a")
    test_crime.evaluate_first_step(5)
    test_crime.evaluate_second_step(aggravating_count=2, mitigating_count=1)
