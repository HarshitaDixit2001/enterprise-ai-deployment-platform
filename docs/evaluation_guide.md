# Evaluation Guide

## Purpose

This guide explains how to run the platform's evaluation pipeline,
interpret its metrics, and understand its release decisions.

The project currently uses a deterministic keyword-based baseline
and a small synthetic customer-feedback dataset. It does not require
a paid AI API.

## 1. Set Up the Environment

From the project root, create and activate a virtual environment if
you have not already done so.

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt