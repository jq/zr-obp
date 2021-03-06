import re

import pytest
import numpy as np

from obp.types import BanditFeedback
from obp.ope import (
    InverseProbabilityWeighting,
    DirectMethod,
    DoublyRobust,
    DoublyRobustWithShrinkage,
    SwitchInverseProbabilityWeighting,
    SwitchDoublyRobust,
    SelfNormalizedDoublyRobust,
)


# prepare instances
ipw = InverseProbabilityWeighting()
dm = DirectMethod()
dr = DoublyRobust()
dr_shrink_0 = DoublyRobustWithShrinkage(lambda_=0)
dr_shrink_max = DoublyRobustWithShrinkage(lambda_=1e10)
sndr = SelfNormalizedDoublyRobust()
switch_ipw_0 = SwitchInverseProbabilityWeighting(tau=0)
switch_ipw_max = SwitchInverseProbabilityWeighting(tau=1e10)
switch_dr_0 = SwitchDoublyRobust(tau=0)
switch_dr_max = SwitchDoublyRobust(tau=1e10)

dr_estimators = [dr, dr_shrink_0, sndr, switch_ipw_0, switch_dr_0]


def test_dr_using_random_evaluation_policy(
    synthetic_bandit_feedback: BanditFeedback, random_action_dist: np.ndarray
) -> None:
    """
    Test the format of dr variants using synthetic bandit data and random evaluation policy
    """
    expected_reward = np.expand_dims(
        synthetic_bandit_feedback["expected_reward"], axis=-1
    )
    action_dist = random_action_dist
    # prepare input dict
    input_dict = {
        k: v
        for k, v in synthetic_bandit_feedback.items()
        if k in ["reward", "action", "pscore", "position"]
    }
    input_dict["action_dist"] = action_dist
    input_dict["estimated_rewards_by_reg_model"] = expected_reward
    # dr estimtors require all arguments
    for estimator in dr_estimators:
        estimated_policy_value = estimator.estimate_policy_value(**input_dict)
        assert isinstance(
            estimated_policy_value, float
        ), f"invalid type response: {estimator}"
    # remove necessary keys
    del input_dict["reward"]
    del input_dict["pscore"]
    del input_dict["action"]
    del input_dict["estimated_rewards_by_reg_model"]
    for estimator in dr_estimators:
        with pytest.raises(
            TypeError,
            match=re.escape(
                "estimate_policy_value() missing 4 required positional arguments: 'reward', 'action', 'pscore', and 'estimated_rewards_by_reg_model'"
            ),
        ):
            _ = estimator.estimate_policy_value(**input_dict)


def test_boundedness_of_sndr_using_random_evaluation_policy(
    synthetic_bandit_feedback: BanditFeedback, random_action_dist: np.ndarray
) -> None:
    """
    Test the boundedness of sndr estimators using synthetic bandit data and random evaluation policy
    """
    expected_reward = np.expand_dims(
        synthetic_bandit_feedback["expected_reward"], axis=-1
    )
    action_dist = random_action_dist
    # prepare input dict
    input_dict = {
        k: v
        for k, v in synthetic_bandit_feedback.items()
        if k in ["reward", "action", "pscore", "position"]
    }
    input_dict["action_dist"] = action_dist
    input_dict["estimated_rewards_by_reg_model"] = expected_reward
    # make pscore too small (to check the boundedness of sndr)
    input_dict["pscore"] = input_dict["pscore"] ** 3
    estimated_policy_value = sndr.estimate_policy_value(**input_dict)
    assert (
        estimated_policy_value <= 2
    ), f"estimated policy value of sndr should be smaller than or equal to 2 (because of its 2-boundedness), but the value is: {estimated_policy_value}"


def test_dr_shrinkage_using_random_evaluation_policy(
    synthetic_bandit_feedback: BanditFeedback, random_action_dist: np.ndarray
) -> None:
    """
    Test the dr shrinkage estimators using synthetic bandit data and random evaluation policy
    """
    expected_reward = np.expand_dims(
        synthetic_bandit_feedback["expected_reward"], axis=-1
    )
    action_dist = random_action_dist
    # prepare input dict
    input_dict = {
        k: v
        for k, v in synthetic_bandit_feedback.items()
        if k in ["reward", "action", "pscore", "position"]
    }
    input_dict["action_dist"] = action_dist
    input_dict["estimated_rewards_by_reg_model"] = expected_reward
    dm_value = dm.estimate_policy_value(**input_dict)
    dr_value = dr.estimate_policy_value(**input_dict)
    dr_shrink_0_value = dr_shrink_0.estimate_policy_value(**input_dict)
    dr_shrink_max_value = dr_shrink_max.estimate_policy_value(**input_dict)
    assert (
        dm_value == dr_shrink_0_value
    ), "DoublyRobustWithShrinkage (lambda=0) should be the same as DirectMethod"
    assert (
        np.abs(dr_value - dr_shrink_max_value) < 1e-5
    ), "DoublyRobustWithShrinkage (lambda=inf) should be almost the same as DoublyRobust"


def test_switch_ipw_using_random_evaluation_policy(
    synthetic_bandit_feedback: BanditFeedback, random_action_dist: np.ndarray
) -> None:
    """
    Test the switch_ipw estimators using synthetic bandit data and random evaluation policy
    """
    expected_reward = np.expand_dims(
        synthetic_bandit_feedback["expected_reward"], axis=-1
    )
    action_dist = random_action_dist
    # prepare input dict
    input_dict = {
        k: v
        for k, v in synthetic_bandit_feedback.items()
        if k in ["reward", "action", "pscore", "position"]
    }
    input_dict["action_dist"] = action_dist
    input_dict["estimated_rewards_by_reg_model"] = expected_reward
    dm_value = dm.estimate_policy_value(**input_dict)
    ipw_value = ipw.estimate_policy_value(**input_dict)
    switch_ipw_0_value = switch_ipw_0.estimate_policy_value(**input_dict)
    switch_ipw_max_value = switch_ipw_max.estimate_policy_value(**input_dict)
    assert (
        dm_value == switch_ipw_0_value
    ), "SwitchIPW (tau=0) should be the same as DirectMethod"
    assert (
        ipw_value == switch_ipw_max_value
    ), "SwitchIPW (tau=1e10) should be the same as IPW"


def test_switch_dr_using_random_evaluation_policy(
    synthetic_bandit_feedback: BanditFeedback, random_action_dist: np.ndarray
) -> None:
    """
    Test the switch_dr using synthetic bandit data and random evaluation policy
    """
    expected_reward = np.expand_dims(
        synthetic_bandit_feedback["expected_reward"], axis=-1
    )
    action_dist = random_action_dist
    # prepare input dict
    input_dict = {
        k: v
        for k, v in synthetic_bandit_feedback.items()
        if k in ["reward", "action", "pscore", "position"]
    }
    input_dict["action_dist"] = action_dist
    input_dict["estimated_rewards_by_reg_model"] = expected_reward
    dm_value = dm.estimate_policy_value(**input_dict)
    dr_value = dr.estimate_policy_value(**input_dict)
    switch_dr_0_value = switch_dr_0.estimate_policy_value(**input_dict)
    switch_dr_max_value = switch_dr_max.estimate_policy_value(**input_dict)
    assert (
        dm_value == switch_dr_0_value
    ), "SwitchDR (tau=0) should be the same as DirectMethod"
    assert (
        dr_value == switch_dr_max_value
    ), "SwitchDR (tau=1e10) should be the same as DoublyRobust"
