class GistPublishError(Exception):
    """Erro ao publicar gist. Carrega o resultado parcial com gist_status de erro."""

    def __init__(self, result):
        self.result = result
        super().__init__("Erro ao publicar gist")
