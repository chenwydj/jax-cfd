# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for jax_cfd.boundaries."""

# TODO(jamieas): Consider updating these tests using the `hypothesis` framework.
from absl.testing import absltest
from absl.testing import parameterized
import jax.numpy as jnp
from jax_cfd.base import boundaries
from jax_cfd.base import grids
from jax_cfd.base import test_util
import numpy as np

BCType = boundaries.BCType


class HomogeneousBoundaryConditionsTest(test_util.TestCase):

  def test_init_usage(self):

    with self.subTest('init 1d'):
      bc = boundaries.HomogeneousBoundaryConditions(
          ((BCType.PERIODIC, BCType.PERIODIC)))
      self.assertEqual(bc.types, (('periodic', 'periodic')))

    with self.subTest('init 2d'):
      bc = boundaries.HomogeneousBoundaryConditions([
          (BCType.PERIODIC, BCType.PERIODIC),
          (BCType.DIRICHLET, BCType.DIRICHLET)
      ])
      self.assertEqual(bc.types, (
          ('periodic', 'periodic'),
          ('dirichlet', 'dirichlet'),
      ))

    with self.subTest('periodic bc utility'):
      bc = boundaries.periodic_boundary_conditions(ndim=3)
      self.assertEqual(bc.types, (
          ('periodic', 'periodic'),
          ('periodic', 'periodic'),
          ('periodic', 'periodic'),
      ))

    with self.subTest('dirichlet bc utility'):
      bc = boundaries.dirichlet_boundary_conditions(ndim=3)
      self.assertEqual(bc.types, (
          ('dirichlet', 'dirichlet'),
          ('dirichlet', 'dirichlet'),
          ('dirichlet', 'dirichlet'),
      ))

    with self.subTest('neumann bc utility'):
      bc = boundaries.neumann_boundary_conditions(ndim=3)
      self.assertEqual(bc.types, (
          ('neumann', 'neumann'),
          ('neumann', 'neumann'),
          ('neumann', 'neumann'),
      ))

    with self.subTest('periodic and dirichlet bc utility'):
      bc = boundaries.periodic_and_dirichlet_boundary_conditions()
      self.assertEqual(bc.types, (
          ('periodic', 'periodic'),
          ('dirichlet', 'dirichlet'),
      ))

    with self.subTest('periodic and neumann bc utility'):
      bc = boundaries.periodic_and_neumann_boundary_conditions()
      self.assertEqual(bc.types, (
          ('periodic', 'periodic'),
          ('neumann', 'neumann'),
      ))

  @parameterized.parameters(
      dict(
          shape=(11,),
          initial_offset=(0.0,),
          step=1,
          offset=(0,),
      ),
      dict(
          shape=(11,),
          initial_offset=(0.0,),
          step=1,
          offset=(1,),
      ),
      dict(
          shape=(11,),
          initial_offset=(0.0,),
          step=1,
          offset=(-1,),
      ),
      dict(
          shape=(11,),
          initial_offset=(0.0,),
          step=1,
          offset=(5,),
      ),
      dict(
          shape=(11,),
          initial_offset=(0.0,),
          step=1,
          offset=(13,),
      ),
      dict(
          shape=(11,),
          initial_offset=(0.0,),
          step=1,
          offset=(31,),
      ),
      dict(
          shape=(11, 12, 17),
          initial_offset=(-0.5, -1.0, 1.0),
          step=0.1,
          offset=(-236, 10001, 3),
      ),
      dict(
          shape=(121,),
          initial_offset=(-0.5,),
          step=1,
          offset=(31,),
      ),
      dict(
          shape=(11, 12, 17),
          initial_offset=(0.5, 0.0, 1.0),
          step=0.1,
          offset=(-236, 10001, 3),
      ),
  )
  def test_shift_periodic(self, shape, initial_offset, step, offset):
    """Test that `shift` returns the expected values for periodic BC."""
    grid = grids.Grid(shape, step)
    data = np.arange(np.prod(shape)).reshape(shape)
    array = grids.GridArray(data, initial_offset, grid)
    bc = boundaries.periodic_boundary_conditions(grid.ndim)

    shifted_array = array
    for axis, o in enumerate(offset):
      shifted_array = bc.shift(shifted_array, o, axis)

    shifted_indices = [(jnp.arange(s) + o) % s for s, o in zip(shape, offset)]
    shifted_mesh = jnp.meshgrid(*shifted_indices, indexing='ij')
    expected_offset = tuple(i + o for i, o in zip(initial_offset, offset))
    expected = grids.GridArray(data[tuple(shifted_mesh)], expected_offset, grid)

    self.assertArrayEqual(shifted_array, expected)

  @parameterized.parameters(
      # Periodic BC
      dict(
          bc_types=((BCType.PERIODIC, BCType.PERIODIC),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          shift_offset=-2,
          expected_data=np.array([13, 14, 11, 12]),
          expected_offset=(-2,),
      ),
      dict(
          bc_types=((BCType.PERIODIC, BCType.PERIODIC),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          shift_offset=-1,
          expected_data=np.array([14, 11, 12, 13]),
          expected_offset=(-1,),
      ),
      dict(
          bc_types=((BCType.PERIODIC, BCType.PERIODIC),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          shift_offset=0,
          expected_data=np.array([11, 12, 13, 14]),
          expected_offset=(0,),
      ),
      dict(
          bc_types=((BCType.PERIODIC, BCType.PERIODIC),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          shift_offset=1,
          expected_data=np.array([12, 13, 14, 11]),
          expected_offset=(1,),
      ),
      dict(
          bc_types=((BCType.PERIODIC, BCType.PERIODIC),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          shift_offset=2,
          expected_data=np.array([13, 14, 11, 12]),
          expected_offset=(2,),
      ),
      # Dirichlet BC
      dict(
          bc_types=((BCType.DIRICHLET, BCType.DIRICHLET),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          shift_offset=-2,
          expected_data=np.array([0, 0, 11, 12]),
          expected_offset=(-2,),
      ),
      dict(
          bc_types=((BCType.DIRICHLET, BCType.DIRICHLET),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          shift_offset=-1,
          expected_data=np.array([0, 11, 12, 13]),
          expected_offset=(-1,),
      ),
      dict(
          bc_types=((BCType.DIRICHLET, BCType.DIRICHLET),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          shift_offset=0,
          expected_data=np.array([11, 12, 13, 14]),
          expected_offset=(0,),
      ),
      dict(
          bc_types=((BCType.DIRICHLET, BCType.DIRICHLET),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          shift_offset=1,
          expected_data=np.array([12, 13, 14, 0]),
          expected_offset=(1,),
      ),
      dict(
          bc_types=((BCType.DIRICHLET, BCType.DIRICHLET),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          shift_offset=2,
          expected_data=np.array([13, 14, 0, 0]),
          expected_offset=(2,),
      ),
      # Neumann BC
      dict(
          bc_types=((BCType.NEUMANN, BCType.NEUMANN),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          shift_offset=-2,
          expected_data=np.array([11, 11, 11, 12]),
          expected_offset=(-2,),
      ),
      dict(
          bc_types=((BCType.NEUMANN, BCType.NEUMANN),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          shift_offset=-1,
          expected_data=np.array([11, 11, 12, 13]),
          expected_offset=(-1,),
      ),
      dict(
          bc_types=((BCType.NEUMANN, BCType.NEUMANN),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          shift_offset=0,
          expected_data=np.array([11, 12, 13, 14]),
          expected_offset=(0,),
      ),
      dict(
          bc_types=((BCType.NEUMANN, BCType.NEUMANN),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          shift_offset=1,
          expected_data=np.array([12, 13, 14, 14]),
          expected_offset=(1,),
      ),
      dict(
          bc_types=((BCType.NEUMANN, BCType.NEUMANN),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          shift_offset=2,
          expected_data=np.array([13, 14, 14, 14]),
          expected_offset=(2,),
      ),
      # Dirichlet / Neumann BC
      dict(
          bc_types=((BCType.DIRICHLET, BCType.NEUMANN),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          shift_offset=-1,
          expected_data=np.array([0, 11, 12, 13]),
          expected_offset=(-1,),
      ),
      dict(
          bc_types=((BCType.DIRICHLET, BCType.NEUMANN),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          shift_offset=1,
          expected_data=np.array([12, 13, 14, 14]),
          expected_offset=(1,),
      ),
  )
  def test_shift_1d(self, bc_types, input_data, input_offset, shift_offset,
                    expected_data, expected_offset):
    grid = grids.Grid(input_data.shape)
    array = grids.GridArray(input_data, input_offset, grid)
    bc = boundaries.HomogeneousBoundaryConditions(bc_types)
    actual = bc.shift(array, shift_offset, axis=0)
    expected = grids.GridArray(expected_data, expected_offset, grid)
    self.assertArrayEqual(actual, expected)

  @parameterized.parameters(
      # Periodic BC
      dict(
          bc_types=((BCType.PERIODIC, BCType.PERIODIC),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          width=-2,
          expected_data=np.array([13, 14, 11, 12, 13, 14]),
          expected_offset=(-2,),
      ),
      dict(
          bc_types=((BCType.PERIODIC, BCType.PERIODIC),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          width=-1,
          expected_data=np.array([14, 11, 12, 13, 14]),
          expected_offset=(-1,),
      ),
      dict(
          bc_types=((BCType.PERIODIC, BCType.PERIODIC),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          width=0,
          expected_data=np.array([11, 12, 13, 14]),
          expected_offset=(0,),
      ),
      dict(
          bc_types=((BCType.PERIODIC, BCType.PERIODIC),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          width=1,
          expected_data=np.array([11, 12, 13, 14, 11]),
          expected_offset=(0,),
      ),
      dict(
          bc_types=((BCType.PERIODIC, BCType.PERIODIC),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          width=2,
          expected_data=np.array([11, 12, 13, 14, 11, 12]),
          expected_offset=(0,),
      ),
      # Dirichlet BC
      dict(
          bc_types=((BCType.DIRICHLET, BCType.DIRICHLET),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          width=-2,
          expected_data=np.array([0, 0, 11, 12, 13, 14]),
          expected_offset=(-2,),
      ),
      dict(
          bc_types=((BCType.DIRICHLET, BCType.DIRICHLET),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          width=-1,
          expected_data=np.array([0, 11, 12, 13, 14]),
          expected_offset=(-1,),
      ),
      dict(
          bc_types=((BCType.DIRICHLET, BCType.DIRICHLET),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          width=0,
          expected_data=np.array([11, 12, 13, 14]),
          expected_offset=(0,),
      ),
      dict(
          bc_types=((BCType.DIRICHLET, BCType.DIRICHLET),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          width=1,
          expected_data=np.array([11, 12, 13, 14, 0]),
          expected_offset=(0,),
      ),
      dict(
          bc_types=((BCType.DIRICHLET, BCType.DIRICHLET),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          width=2,
          expected_data=np.array([11, 12, 13, 14, 0, 0]),
          expected_offset=(0,),
      ),
      # Neumann BC
      dict(
          bc_types=((BCType.NEUMANN, BCType.NEUMANN),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          width=-2,
          expected_data=np.array([11, 11, 11, 12, 13, 14]),
          expected_offset=(-2,),
      ),
      dict(
          bc_types=((BCType.NEUMANN, BCType.NEUMANN),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          width=-1,
          expected_data=np.array([11, 11, 12, 13, 14]),
          expected_offset=(-1,),
      ),
      dict(
          bc_types=((BCType.NEUMANN, BCType.NEUMANN),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          width=0,
          expected_data=np.array([11, 12, 13, 14]),
          expected_offset=(0,),
      ),
      dict(
          bc_types=((BCType.NEUMANN, BCType.NEUMANN),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          width=1,
          expected_data=np.array([11, 12, 13, 14, 14]),
          expected_offset=(0,),
      ),
      dict(
          bc_types=((BCType.NEUMANN, BCType.NEUMANN),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          width=2,
          expected_data=np.array([11, 12, 13, 14, 14, 14]),
          expected_offset=(0,),
      ),
      # Dirichlet / Neumann BC
      dict(
          bc_types=((BCType.DIRICHLET, BCType.NEUMANN),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          width=-1,
          expected_data=np.array([0, 11, 12, 13, 14]),
          expected_offset=(-1,),
      ),
      dict(
          bc_types=((BCType.DIRICHLET, BCType.NEUMANN),),
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          width=1,
          expected_data=np.array([11, 12, 13, 14, 14]),
          expected_offset=(0,),
      ),
  )
  def test_pad_1d(self, bc_types, input_data, input_offset, width,
                  expected_data, expected_offset):
    grid = grids.Grid(input_data.shape)
    array = grids.GridArray(input_data, input_offset, grid)
    bc = boundaries.HomogeneousBoundaryConditions(bc_types)
    actual = bc._pad(array, width, axis=0)
    expected = grids.GridArray(expected_data, expected_offset, grid)
    self.assertArrayEqual(actual, expected)

  @parameterized.parameters(
      dict(
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          width=-1,
          expected_data=np.array([12, 13, 14]),
          expected_offset=(1,),
      ),
      dict(
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          width=0,
          expected_data=np.array([11, 12, 13, 14]),
          expected_offset=(0,),
      ),
      dict(
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          width=1,
          expected_data=np.array([11, 12, 13]),
          expected_offset=(0,),
      ),
      dict(
          input_data=np.array([11, 12, 13, 14]),
          input_offset=(0,),
          width=2,
          expected_data=np.array([11, 12]),
          expected_offset=(0,),
      ),
  )
  def test_trim_1d(self, input_data, input_offset, width, expected_data,
                   expected_offset):
    grid = grids.Grid(input_data.shape)
    array = grids.GridArray(input_data, input_offset, grid)
    bc = boundaries.periodic_boundary_conditions(grid.ndim)
    # Note: trim behavior does not depend on bc type
    actual = bc._trim(array, width, axis=0)
    expected = grids.GridArray(expected_data, expected_offset, grid)
    self.assertArrayEqual(actual, expected)

  def test_has_all_periodic_boundary_conditions(self):
    grid = grids.Grid((10, 10))
    array = grids.GridArray(np.zeros((10, 10)), (0.5, 0.5), grid)
    periodic_bc = boundaries.periodic_boundary_conditions(ndim=2)
    nonperiodic_bc = boundaries.periodic_and_dirichlet_boundary_conditions()

    with self.subTest('returns True'):
      c = grids.GridVariable(array, periodic_bc)
      v = (grids.GridVariable(array, periodic_bc),
           grids.GridVariable(array, periodic_bc))
      self.assertTrue(boundaries.has_all_periodic_boundary_conditions(c, *v))

    with self.subTest('returns False'):
      c = grids.GridVariable(array, periodic_bc)
      v = (grids.GridVariable(array, periodic_bc),
           grids.GridVariable(array, nonperiodic_bc))
      self.assertFalse(boundaries.has_all_periodic_boundary_conditions(c, *v))

  def test_get_pressure_bc_from_velocity(self):
    grid = grids.Grid((10, 10))
    u_array = grids.GridArray(jnp.zeros(grid.shape), (1, 0.5), grid)
    v_array = grids.GridArray(jnp.zeros(grid.shape), (0.5, 1), grid)
    velocity_bc = boundaries.periodic_and_dirichlet_boundary_conditions()
    v = (grids.GridVariable(u_array, velocity_bc),
         grids.GridVariable(v_array, velocity_bc))
    pressure_bc = boundaries.get_pressure_bc_from_velocity(v)
    self.assertEqual(pressure_bc.types, ((BCType.PERIODIC, BCType.PERIODIC),
                                         (BCType.NEUMANN, BCType.NEUMANN)))


if __name__ == '__main__':
  absltest.main()
