"""Run the whole project from start to finish."""

import build_dataset
import step1_explore
import step2_learn
import step3_discover
import step4_mystery
import step5_lifespan
import build_demo

if __name__ == "__main__":
    build_dataset.main()
    step1_explore.main()
    step2_learn.main()
    step3_discover.main()
    step4_mystery.main()
    step5_lifespan.main()
    build_demo.main()
    print("\nDone. Charts are in outputs/figures, the rules are in outputs/,")
    print("and the interactive page is demo/index.html.")
