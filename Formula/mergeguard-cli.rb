class MergeguardCli < Formula
  include Language::Python::Virtualenv

  desc "Deterministic review-readiness checks for AI-assisted pull requests"
  homepage "https://github.com/krpraveen0/mergeguard"
  url "https://files.pythonhosted.org/packages/b0/93/6640567ec6688462f0f7b52d93711827226042fe89f7345c4d078d7eae01/mergeguard_cli-0.1.0.tar.gz"
  sha256 "6bcebb09f0885b88b7dbbf6db5d07cadea911598f9554eb4fef0df9d10baba31"
  license "Apache-2.0"

  depends_on "python-setuptools" => :build
  depends_on "python@3.14"

  def install
    venv = virtualenv_create(libexec, "python3.14")
    venv.pip_install_and_link buildpath, build_isolation: false
  end

  test do
    assert_match "usage:", shell_output("#{bin}/mergeguard --help")
  end
end
