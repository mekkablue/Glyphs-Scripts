# -*- coding: utf-8 -*-
from __future__ import print_function

__doc__ = """
Unit tests for the mekkablue scripts. Glyphs exposes every top-level test_*
function in the test sidebar and can run either one test or the complete file.
"""

import os
import sys

import pytest

unitTestDirectory = os.path.dirname(__file__)
if unitTestDirectory not in sys.path:
	sys.path.insert(0, unitTestDirectory)

from _Tests import AxisChecks, CodeCheckerChecks, CompareChecks, GeometryChecks, SyntaxChecks  # noqa: E402


# Axis helpers

def test_axis_value_lookup():
	AxisChecks.checkAxisValueLookup()


def test_axis_extreme_native_values():
	AxisChecks.checkExtremeNativeValues()


def test_axis_extreme_values_of_empty_collections():
	AxisChecks.checkExtremeValuesOfEmptyCollections()


def test_axis_extreme_weight_classes():
	AxisChecks.checkExtremeWeightClasses()


def test_axis_coefficient_round_trip():
	AxisChecks.checkCoefficientRoundTrip()


# Font comparison helpers

def test_compare_lists_returns_unique_items():
	CompareChecks.checkCompareListsReturnsUniqueItems()


def test_compare_lists_can_ignore_empty_items():
	CompareChecks.checkCompareListsCanIgnoreEmptyItems()


def test_compare_cleanup_shortens_and_flattens_content():
	CompareChecks.checkCleanupShortensAndFlattensContent()


def test_compare_count_report():
	CompareChecks.checkCompareCountReport()


# Geometry helpers

def test_geometry_bezier_endpoints_and_midpoint():
	GeometryChecks.checkBezierEndpointsAndMidpoint()


def test_geometry_divide_tolerates_zero():
	GeometryChecks.checkDivideToleratesZero()


def test_geometry_angle():
	GeometryChecks.checkAngle()


def test_geometry_normalized_coordinate():
	GeometryChecks.checkNormalizedCoordinate()


def test_geometry_normalized_coordinate_accounts_for_italic_angle():
	GeometryChecks.checkNormalizedCoordinateAccountsForItalicAngle()


def test_geometry_normalized_coordinate_with_empty_bounds():
	GeometryChecks.checkNormalizedCoordinateWithEmptyBounds()


def test_geometry_normalized_move():
	GeometryChecks.checkNormalizedMove()


def test_geometry_normalized_move_rejects_unusable_layers():
	GeometryChecks.checkNormalizedMoveRejectsUnusableLayers()


# Repository checks

def test_scripts_have_valid_python_syntax():
	SyntaxChecks.checkScriptsCompile()


def test_scripts_have_no_new_ruff_undefined_names():
	CodeCheckerChecks.checkRuffUndefinedNames()
