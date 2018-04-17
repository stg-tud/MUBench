<?php


use MuBench\ReviewSite\Models\Detector;
use MuBench\ReviewSite\Models\Reviewer;
use MuBench\ReviewSite\ViewExtensions\AnonymousViewExtension;

require_once "SlimTestCase.php";

class AnonymousViewExtensionTest extends SlimTestCase
{
    /** @var  Detector */
    private $detector;

    /** @var  Reviewer */
    private $reviewer;

    private $blind_mode_settings;

    public function setUp()
    {
        parent::setUp();
        $this->detector = Detector::create(['muid' => '-d-']);
        $this->reviewer = Reviewer::create(['name' => 'bar']);
        $this->detector_blind_names = array('-d-' => 'foo');
        $this->blind_mode_settings = [
            'enabled' => false,
            'detector_blind_names' => array('-d-' => 'foo')
        ];
        $this->container->settings['blind_mode'] = $this->blind_mode_settings;
    }

    public function test_blinded_detectorName()
    {
        $this->enable_blind_mode();
        $anonymousViewExtension = new AnonymousViewExtension($this->container);

        self::assertEquals('foo', $anonymousViewExtension->getDetectorName($this->detector->muid));
    }

    public function test_not_blinded_detectorName()
    {
        $anonymousViewExtension = new AnonymousViewExtension($this->container);

        self::assertEquals($this->detector->muid, $anonymousViewExtension->getDetectorName($this->detector->muid));
    }

    public function test_blinded_detectorPathId()
    {
        $this->enable_blind_mode();
        $anonymousViewExtension = new AnonymousViewExtension($this->container);

        self::assertEquals($this->detector->id, $anonymousViewExtension->getDetectorPathId($this->detector));
    }

    public function test_not_blinded_detectorPathId()
    {
        $anonymousViewExtension = new AnonymousViewExtension($this->container);

        self::assertEquals($this->detector->muid, $anonymousViewExtension->getDetectorPathId($this->detector));
    }

    public function test_blinded_reviewerName()
    {
        $this->enable_blind_mode();
        $anonymousViewExtension = new AnonymousViewExtension($this->container);

        self::assertEquals("reviewer-{$this->reviewer->id}" , $anonymousViewExtension->getReviewerName($this->reviewer));
    }

    public function test_not_blinded_reviewerName()
    {
        $anonymousViewExtension = new AnonymousViewExtension($this->container);

        self::assertEquals($this->reviewer->name , $anonymousViewExtension->getReviewerName($this->reviewer));
    }

    public function test_blinded_reviewerPathId()
    {
        $this->enable_blind_mode();
        $anonymousViewExtension = new AnonymousViewExtension($this->container);

        self::assertEquals($this->reviewer->id , $anonymousViewExtension->getReviewerPathId($this->reviewer));
    }

    public function test_not_blinded_reviewerPathId()
    {
        $anonymousViewExtension = new AnonymousViewExtension($this->container);

        self::assertEquals($this->reviewer->name , $anonymousViewExtension->getReviewerPathId($this->reviewer));
    }

    private function enable_blind_mode()
    {
        $this->blind_mode_settings['enabled'] = true;
        $this->container->settings['blind_mode'] = $this->blind_mode_settings;
    }
}
