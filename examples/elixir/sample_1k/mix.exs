defmodule SampleElixir.MixProject do
  use Mix.Project

  def project do
    [
      app: :sample_elixir,
      version: "1.0.0",
      elixir: "~> 1.16",
      deps: deps()
    ]
  end

  defp deps, do: []
end
