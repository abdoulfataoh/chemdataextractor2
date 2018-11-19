from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import six

from .base_model import BaseModel, StringType, ListType, ModelType
from .parse.units.temperature import TemperatureModel

log = logging.getLogger(__name__)


class UvvisPeak(BaseModel):
    #: Peak value, i.e. wavelength
    value = StringType()
    #: Peak value units
    units = StringType(contextual=True)
    # Extinction value
    extinction = StringType()
    # Extinction units
    extinction_units = StringType(contextual=True)
    # Peak shape information (e.g. shoulder, broad)
    shape = StringType()


class UvvisSpectrum(BaseModel):
    solvent = StringType(contextual=True)
    temperature = StringType(contextual=True)
    temperature_units = StringType(contextual=True)
    concentration = StringType(contextual=True)
    concentration_units = StringType(contextual=True)
    apparatus = StringType(contextual=True)
    peaks = ListType(ModelType(UvvisPeak))


class IrPeak(BaseModel):
    value = StringType()
    units = StringType(contextual=True)
    strength = StringType()
    bond = StringType()


class IrSpectrum(BaseModel):
    solvent = StringType(contextual=True)
    temperature = StringType(contextual=True)
    temperature_units = StringType(contextual=True)
    concentration = StringType(contextual=True)
    concentration_units = StringType(contextual=True)
    apparatus = StringType(contextual=True)
    peaks = ListType(ModelType(IrPeak))


class NmrPeak(BaseModel):
    shift = StringType()
    intensity = StringType()
    multiplicity = StringType()
    coupling = StringType()
    coupling_units = StringType(contextual=True)
    number = StringType()
    assignment = StringType()


class NmrSpectrum(BaseModel):
    nucleus = StringType(contextual=True)
    solvent = StringType(contextual=True)
    frequency = StringType(contextual=True)
    frequency_units = StringType(contextual=True)
    standard = StringType(contextual=True)
    temperature = StringType(contextual=True)
    temperature_units = StringType(contextual=True)
    concentration = StringType(contextual=True)
    concentration_units = StringType(contextual=True)
    apparatus = StringType(contextual=True)
    peaks = ListType(ModelType(NmrPeak))


# class MeltingPoint(BaseModel):
#     """A melting point measurement."""
#     value = StringType()
#     units = StringType(contextual=True)
#     solvent = StringType(contextual=True)
#     concentration = StringType(contextual=True)
#     concentration_units = StringType(contextual=True)
#     apparatus = StringType(contextual=True)


class MeltingPoint(TemperatureModel):
    solvent = StringType(contextual=True)
    concentration = StringType(contextual=True)
    concentration_units = StringType(contextual=True)
    apparatus = StringType(contextual=True)


class GlassTransition(BaseModel):
    """A glass transition temperature."""
    value = StringType()
    units = StringType(contextual=True)
    method = StringType(contextual=True)
    concentration = StringType(contextual=True)
    concentration_units = StringType(contextual=True)


class QuantumYield(BaseModel):
    """A quantum yield measurement."""
    value = StringType()
    units = StringType(contextual=True)
    solvent = StringType(contextual=True)
    type = StringType(contextual=True)
    standard = StringType(contextual=True)
    standard_value = StringType(contextual=True)
    standard_solvent = StringType(contextual=True)
    concentration = StringType(contextual=True)
    concentration_units = StringType(contextual=True)
    temperature = StringType(contextual=True)
    temperature_units = StringType(contextual=True)
    apparatus = StringType(contextual=True)


class FluorescenceLifetime(BaseModel):
    """A fluorescence lifetime measurement."""
    value = StringType()
    units = StringType(contextual=True)
    solvent = StringType(contextual=True)
    concentration = StringType(contextual=True)
    concentration_units = StringType(contextual=True)
    temperature = StringType(contextual=True)
    temperature_units = StringType(contextual=True)
    apparatus = StringType(contextual=True)


class ElectrochemicalPotential(BaseModel):
    """An oxidation or reduction potential, from cyclic voltammetry."""
    value = StringType()
    units = StringType(contextual=True)
    type = StringType(contextual=True)
    solvent = StringType(contextual=True)
    concentration = StringType(contextual=True)
    concentration_units = StringType(contextual=True)
    temperature = StringType(contextual=True)
    temperature_units = StringType(contextual=True)
    apparatus = StringType(contextual=True)


class Compound(BaseModel):
    names = ListType(StringType())
    labels = ListType(StringType())
    roles = ListType(StringType())
    nmr_spectra = ListType(ModelType(NmrSpectrum))
    ir_spectra = ListType(ModelType(IrSpectrum))
    uvvis_spectra = ListType(ModelType(UvvisSpectrum))
    melting_points = ListType(ModelType(MeltingPoint))
    glass_transitions = ListType(ModelType(GlassTransition))
    quantum_yields = ListType(ModelType(QuantumYield))
    fluorescence_lifetimes = ListType(ModelType(FluorescenceLifetime))
    electrochemical_potentials = ListType(ModelType(ElectrochemicalPotential))

    def merge(self, other):
        """Merge data from another Compound into this Compound."""
        log.debug('Merging: %s and %s' % (self.serialize(), other.serialize()))
        for k in self.keys():
            for new_item in other[k]:
                if new_item not in self[k]:
                    self[k].append(new_item)
        log.debug('Result: %s' % self.serialize())
        return self

    def merge_contextual(self, other):
        """Merge in contextual info from a template Compound."""
        # TODO: This is currently dependent on our data model? Make more robust to schema changes
        # Currently we assume all lists at Compound level, with 1 further potential nested level of lists
        for k in self.keys():
            # print('key: %s' % k)
            for item in self[k]:
                # print('item: %s' % item)
                for other_item in other.get(k, []):
                    # Skip text properties (don't merge names, labels, roles)
                    if isinstance(other_item, six.text_type):
                        continue
                    for otherk in other_item.keys():
                        if isinstance(other_item[otherk], list):
                            if len(other_item[otherk]) > 0 and len(item[otherk]) > 0:
                                other_nested_item = other_item[otherk][0]
                                for othernestedk in other_nested_item.keys():
                                    for nested_item in item[otherk]:
                                        if not nested_item[othernestedk]:
                                            nested_item[othernestedk] = other_nested_item[othernestedk]
                        elif not item[otherk]:
                            item[otherk] = other_item[otherk]
        log.debug('Result: %s' % self.serialize())
        return self

    @property
    def is_unidentified(self):
        if not self.names and not self.labels:
            return True
        return False

    # @property
    # def is_contextual(self):
    #     for k in self:
    #         # Not contextual if we have any names or labels
    #         if k in {'names', 'labels'}:
    #             return False
    #     return super(Compound, self).is_contextual


    @property
    def is_id_only(self):
        """Return True if identifier information only."""
        for key, value in self.items():
            if key not in {'names', 'labels', 'roles'} and value:
                return False
        if self.names or self.labels:
            return True
        return False
